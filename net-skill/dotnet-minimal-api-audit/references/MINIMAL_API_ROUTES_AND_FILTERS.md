# Minimal API Routes and Filters Reference

## Route Registration Patterns

```csharp
// Basic mapping
app.MapGet("/api/users", (UserService svc) => svc.GetAll());
app.MapPost("/api/users", ([FromBody] UserDto dto, UserService svc) => svc.Create(dto));

// Parameterized routes
app.MapGet("/api/users/{id:int}", (int id, UserService svc) => svc.GetById(id));
app.MapDelete("/api/users/{id}", (string id, UserService svc) => svc.Delete(id));

// File upload
app.MapPost("/api/upload", async (IFormFile file) => { ... });
```

## Endpoint Filters

```csharp
app.MapPost("/api/admin", ([FromBody] AdminCommand cmd) => ...)
   .AddEndpointFilter(async (context, next) => {
       if (!context.HttpContext.User.IsInRole("Admin"))
           return Results.Unauthorized();
       return await next(context);
   });
```

### Audit Checklist

- [ ] Every admin/sensitive endpoint has an authorization filter.
- [ ] Filters are applied via `AddEndpointFilter` or `AddEndpointFilterFactory`, not just middleware.
- [ ] Filter ordering does not allow bypass by early returns.
