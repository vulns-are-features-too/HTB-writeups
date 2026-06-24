# Phoenix Pipeline

## Session puzzling

### Session exploit

`exploit_session_puzzling.py` is registering the admin user and getting a session

### Session vulnerability

From `app/index.php`, we find that the vulnerable function is `AuthController@register`.

In `AuthController::register()`, we see a block commented `// Set the session so user can login immediately after registration`.
This session setter is done before any actual authentication check is done, so the attacker easily gets the session even if their password was incorrect.

### Session Fix

The fix is simply to move that block further down the function, after all auth checks are done.

```php
<?php

public static function register() {
    $db = Database::getInstance()->getConnection();
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';
    $area = $_POST['area'] ?? '';
    
    // FIX: remove this
    // // Set the session so user can login immediately after registration
    // $_SESSION['username'] = $username;
    // $_SESSION['area'] = $area;
    
    $stmt = $db->prepare('SELECT * FROM users WHERE username = ?');
    $stmt->execute([$username]);
    if ($stmt->fetch()) {
        header('Location: /challenge/username-exists');
        exit;
    }
    
    $hash = password_hash($password, PASSWORD_DEFAULT);
    $stmt = $db->prepare('INSERT INTO users (username, password, role, area) VALUES (?, ?, ?, ?)');
    $stmt->execute([$username, $hash, 'operator', $area]);
    header('Location: /challenge/operator');

    // FIX: MOVED HERE
    // Set the session so user can login immediately after registration
    $_SESSION['username'] = $username;
    $_SESSION['area'] = $area;

    exit;
}
```

## File upload

### File upload exploit

`exploit_file_upload.py` is exploiting a race condition in the file upload functionality in the `/report` API to upload a backdoor `shell.php`.
The shell is to be placed at `{TARGET}/uploads/temp_{md5_hash}_{formatted_date}.php`.

In `race_once()`, `check_thread()` (using `hit_shell()`) is called right after `upload_thread()` (using `upload_file()`) before joining the 2 threads, and RCE is executed in `hit_shell()` where the payload has the chance to do some work (like persistence) before the upload flow is done.

### File upload vulnerability

From `app/index.php`, we find that the vulnerable function is `OperatorController@submitReport`.

The function:
1. Gets the file data from the request
2. Saves the data to a temp file whose name is in the request's `tmp_name` field
3. Renames the file to `$tempfile = __DIR__ . '/../uploads/temp_' . $rand . '_' . $date . '.' . $ext;`
4. Checks the MIME type on the file, making sure it's an image, deleting non-image files
5. Checks that the file extension is 1 of the white-listed image extensions, deleting unmatched files
6. Moves that file to a final destination `$final`

The vulnerability here is that the attacker can access the file before its final state, specifically right after step 3.

### File upload fix

The solution is to remove usage of `$tempfile`, keeping only the file rename, while 

```php
<?php

public static function submitReport() {
    // [snip]
    
    $original = $_FILES['photo']['name'];
    $ext = strtolower(pathinfo($original, PATHINFO_EXTENSION));
    $tmp_name = $_FILES['photo']['tmp_name'];
    $date = date('Y_m_d');
    $rand = md5($original);
    // $tempfile = __DIR__ . '/../uploads/temp_' . $rand . '_' . $date . '.' . $ext;
    
    // FIX: no need for the $tempfile
    // if (!move_uploaded_file($tmp_name, $tempfile)) {
    //     $showFormWithError('Failed to upload file. Please try again.');
    //     return;
    // }
    
    $finfo = finfo_open(FILEINFO_MIME_TYPE);
    $mime = finfo_file($finfo, $tmp_name);
    finfo_close($finfo);
    
    if (strpos($mime, 'image/') !== 0) {
        unlink($tmp_name); 
        $showFormWithError('Invalid file type. Only image files are allowed.');
        return;
    }

    $allowed = ['jpg','jpeg','png','gif','bmp','webp'];
    if (!in_array($ext, $allowed)) {
        unlink($tmp_name);  
        $showFormWithError('Invalid file extension. Only image files (JPG, PNG, GIF, BMP, WEBP) are allowed.');
        return;
    }


    $infra_name = self::getInfraName($infra_id);
    $final = __DIR__ . '/../uploads/documentation_' . $area . '_' . preg_replace('/\W/','',$infra_name) . "_" . $rand . '_' . $date . '.' . $ext;
    
    if (!move_uploaded_file($tmp_name, $final)) {
        unlink($tmp_name); 
        $showFormWithError('Failed to save file. Please try again.');
        return;
    }
    
    // [snip]
}
```
