# OpenAPI / Swagger Exposure Reference

## Common Exposure Points

```csharp
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}
```

### Risks

- Production environments accidentally enable Swagger UI.
- Internal DTOs with sensitive fields are exposed in OpenAPI schema.
- Swagger UI allows direct API invocation without authentication.

## Audit Checklist

- [ ] `UseSwagger()` / `UseSwaggerUI()` are conditional on non-production environments.
- [ ] `[SwaggerIgnore]` or `[JsonIgnore]` is applied to sensitive fields.
- [ ] Swagger UI endpoints (`/swagger`) are protected by authentication middleware.
- [ ] `OpenApiDocument` does not include admin/internal endpoints.
