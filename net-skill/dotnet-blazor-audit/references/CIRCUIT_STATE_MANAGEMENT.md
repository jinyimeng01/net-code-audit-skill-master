# Circuit State Management Reference

## Blazor Server Circuit Lifecycle

```csharp
public class MyCircuitHandler : CircuitHandler
{
    public override Task OnCircuitOpenedAsync(Circuit circuit, CancellationToken cancellationToken)
    {
        // Circuit opened per browser tab
        return base.OnCircuitOpenedAsync(circuit, cancellationToken);
    }
}
```

## Risks

| Risk | Description |
|------|-------------|
| Session fixation | Circuit ID predictable or reused across sessions |
| State leakage | `AuthenticationStateProvider` caches data shared across Circuits |
| Memory exhaustion | Large objects stored in Circuit scope never released |
| Reconnection abuse | ` circuitOptions.DetailedErrors` leaks stack traces |

## Audit Checklist

- [ ] `CircuitOptions.DetailedErrors` is disabled in production.
- [ ] `CircuitHandler` does not store per-user sensitive data in static fields.
- [ ] `AuthenticationStateProvider` refreshes state per Circuit.
- [ ] Reconnection timeout (`circuitOptions.DisconnectedCircuitMaxRetained`) is reasonable.
