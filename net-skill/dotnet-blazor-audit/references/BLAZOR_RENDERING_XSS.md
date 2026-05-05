# Blazor Rendering and XSS Reference

## Safe vs Unsafe Rendering

| Safe | Unsafe |
|------|--------|
| `@userInput` (Razor auto-encodes) | `@((MarkupString)userInput)` |
| `@bind-value="model.Property"` | `@Html.Raw(userInput)` in `_Host.cshtml` |
| `RenderTreeBuilder.AddContent` | `builder.AddMarkupContent` with user input |

## Component Parameters

```razor
@code {
    [Parameter]
    public string Title { get; set; }
}
```

- `Title` is safely encoded when rendered as `@Title`.
- `Title` is dangerous if passed to `MarkupString` or JS Interop.

## Audit Checklist

- [ ] No `MarkupString` usage with user-controlled data.
- [ ] No `innerHTML` assignments via JS Interop.
- [ ] `_Host.cshtml` does not use `@Html.Raw` with dynamic content.
- [ ] Event callbacks (`@onclick`) do not execute user-provided script.
