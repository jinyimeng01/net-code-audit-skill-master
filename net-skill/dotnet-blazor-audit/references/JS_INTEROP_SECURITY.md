# JS Interop Security Reference

## IJSRuntime Patterns

```csharp
// Safe: calling a known JS function
await JS.InvokeVoidAsync("console.log", message);

// Dangerous: user input as function name or argument to eval
await JS.InvokeVoidAsync(userFunction, args);
await JS.InvokeVoidAsync("eval", userCode);
```

## JSInvokable Attributes

```csharp
[JSInvokable]
public void ProcessData(string input) { ... }
```

- Any JS code in the browser can call `[JSInvokable]` methods.
- Must validate `input` as if it came from an untrusted HTTP request.

## Audit Checklist

- [ ] `InvokeAsync` / `InvokeVoidAsync` do not use user input as the function name.
- [ ] No `eval` or `new Function` calls via JS Interop.
- [ ] `[JSInvokable]` methods perform input validation.
- [ ] JS interop calls do not pass DOM selectors constructed from user input.
