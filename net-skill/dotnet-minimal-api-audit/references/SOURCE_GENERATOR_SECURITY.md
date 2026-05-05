# Source Generator Security Reference

## Overview

ASP.NET Core 7+ uses `RequestDelegateGenerator` to compile Minimal API endpoints at build time. Generated code may:

- Bypass runtime validation if source generator misinterprets attributes.
- Expose internal types through OpenAPI metadata.

## Audit Points

1. Check `Generated/<Assembly>.Requests.g.cs` for generated `RequestDelegate` implementations.
2. Verify that `[FromServices]` is not confused with `[FromBody]` in generated code.
3. Ensure `JsonSerializerContext` (source-generated JSON serializer) does not expose internal DTOs.
4. Check for `unsafe` blocks or pointer arithmetic in generated code (rare but possible in custom generators).

## Risk Scenarios

| Scenario | Risk |
|---|---|
| Custom source generator parses user input | Input validation happens at compile time, runtime input unchecked |
| `JsonSerializerContext` includes internal types | Schema exposure through OpenAPI |
