# Transport and CORS Reference

## Transport Configuration

```csharp
builder.Services.AddSignalR()
    .AddJsonProtocol(options =>
    {
        options.PayloadSerializerOptions.PropertyNamingPolicy = null;
    });
```

## CORS for SignalR

```csharp
app.UseCors(policy =>
    policy.AllowAnyOrigin()        // Dangerous
          .AllowAnyHeader()
          .AllowAnyMethod()
          .AllowCredentials());     // Cannot combine with AllowAnyOrigin
```

### Risks

- `AllowAnyOrigin` + `AllowCredentials` causes CORS policy error in modern browsers but may be bypassed in older clients.
- Missing Origin validation on WebSocket upgrade allows cross-site WebSocket hijacking.

## Audit Checklist

- [ ] CORS policy does not use `AllowAnyOrigin` with `AllowCredentials`.
- [ ] WebSocket upgrade requests validate the `Origin` header.
- [ ] LongPolling transport has message size and timeout limits.
- [ ] Server-Sent Events (SSE) endpoints are protected by authentication.
