# Message and Group Security Reference

## Group Management

```csharp
public async Task JoinGroup(string groupName)
{
    await Groups.AddToGroupAsync(Context.ConnectionId, groupName);
}
```

### Risks

- User-controlled `groupName` allows joining arbitrary groups.
- No validation on whether the user is allowed to join that group.

## Message Broadcasting

```csharp
public async Task SendMessage(string groupName, string message)
{
    await Clients.Group(groupName).SendAsync("ReceiveMessage", message);
}
```

### Risks

- `groupName` not validated → message sent to wrong group (information disclosure or spoofing).
- `message` not encoded → XSS in receiving clients.

## Audit Checklist

- [ ] Group names are validated against an allowlist or user-owned groups.
- [ ] `Clients.Group` / `Clients.User` target selectors are not user-controlled without validation.
- [ ] Messages are encoded/validated before broadcasting.
- [ ] Hub methods do not echo user input back without encoding.
