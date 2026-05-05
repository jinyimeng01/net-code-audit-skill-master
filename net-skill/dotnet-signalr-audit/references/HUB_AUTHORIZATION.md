# Hub Authorization Reference

## Attribute-Based Auth

```csharp
[Authorize(Roles = "Admin")]
public class AdminHub : Hub
{
    [AllowAnonymous]
    public Task PublicMethod() => ...; // Dangerous if admin hub has public methods

    public Task AdminAction() => ...; // Requires Admin role
}
```

## Programmatic Auth

```csharp
public override async Task OnConnectedAsync()
{
    if (!Context.User.Identity.IsAuthenticated)
    {
        Context.Abort();
        return;
    }
    await base.OnConnectedAsync();
}
```

## Audit Checklist

- [ ] Every Hub method that performs sensitive operations has `[Authorize]`.
- [ ] `[AllowAnonymous]` is not used on admin Hub methods.
- [ ] `OnConnectedAsync` validates authentication before group assignment.
- [ ] `IUserIdProvider` does not allow user ID spoofing.
