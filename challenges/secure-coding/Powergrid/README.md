# Powergrid

## Exploit

In `exploit/solver.py`, we find that the payload is in the `username` field of the `/api/auth/register` endpoint.
The payload contains is `{username}|{password_hash}|admin`, where the `admin` can be a username, a role, or something similar.
The key here is the use of `|`.

## Endpoint

Following the solver, we check the `register` endpoint.

```js
// Register
router.post('/register', (req, res) => {
    const { username, password } = req.body;

    if (!username || !password) {
        return res.status(400).json({ success: false, error: 'Username and password required' });
    }

    const success = addUser(username, password, 'operator');
    if (!success) {
        return res.status(400).json({ success: false, error: 'Username already exists or registration failed' });
    }

    // Auto-login after registration
    const user = authenticateUser(username, password);
    if (user) {
        req.session.username = user.username;
        req.session.role = user.role;
    }

    res.json({ success: true, message: 'Registration successful' });
});
```

Nothing here is immediately suspicious.
Since the exploit is in the act of registration, and the solver had to log in after registration, `addUser()` seems more likely to be an issue than `authenticateUser()` used for auto-login, so we check the `addUser()` function imported from `'../utils/db.js'`.

## Database

In `addUser()`:

1. All users are read from the DB
2. The username is checked, and fails the flow for existing usernames
3. The new user is created & added to the list

While this is not like the usual SQL code, there's no immediate vulnerability yet.

We can check how the DB works in `readUsers()` and `writeUsers()`.
We find that the database is just a text file, where each user has the form `${user.username}|${user.password}|${user.role}`.
This explains the payload - the username field simply contains the whole user object, including the admin role.

## Fix

While the real fix would be to use a better database, we can simply detect and block the attack.

```js
// Register
router.post('/register', (req, res) => {
    const { username, password } = req.body;

    if (!username || !password) {
        return res.status(400).json({ success: false, error: 'Username and password required' });
    }

    // FIX: detect and block injection
    if(username.includes("|") || password.includes("|")) {
        return res.status(401).json({ success: false, error: 'NOPE' });
    }
    // FIX: detect and block injection

    const success = addUser(username, password, 'operator');
    if (!success) {
        return res.status(400).json({ success: false, error: 'Username already exists or registration failed' });
    }

    // snip
});
```
