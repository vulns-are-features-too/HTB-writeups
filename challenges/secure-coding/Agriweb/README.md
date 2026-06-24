# Agriweb

## Exploit

From `__proto__` and `prototype`+`constructor` we can tell this is prototype pollution.

The vulnerable API is in `update_profile()`: `/api/profile` and its JSON body.

## Vulnerability

In `routes/profile.js` `function updateProfile()`, there's usage of `deepMerge`.
Object merges are known to be sources of prototype pollution, so we need to patch the `deepMerge` function.

## Fix

A simple solution would be to blacklist merging of known dangerous properties.
An example of such a fix can be found with a quick search like "javascript merge prototype pollution": https://github.com/swordev/merge/pull/38/files

```js
function deepMerge(target, source) {
  for (let key in source) {
    // FIX: blacklist
    if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
        continue;
    }
    // FIX: blacklist
    if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
      if (!target[key]) target[key] = {};
      deepMerge(target[key], source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}
```

