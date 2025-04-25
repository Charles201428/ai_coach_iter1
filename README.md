

## 1. Base URL & Health Check

- **Service URL**  
  ```
  https://ai-coach-iter1-2jzhdhuvoa-uc.a.run.app
  ```
- **Health endpoint**  
  ```http
  GET /healthz
  Response: { "status": "ok" }
  ```

---

## 2. Authentication

1. **Obtain a Supabase JWT**  
   Front‑end must use Supabase‑JS (or equivalent) to sign in:
   ```js
   const { data, error } = await supabase.auth.signInWithPassword({
     email: "alice@example.com",
     password: "supersecret"
   });
   const jwt = data.session.access_token;
   ```
2. **Include the JWT in requests**  
   ```
   Authorization: Bearer <jwt>
   ```

---

## 3. CORS

- **Temporary**: all origins are currently allowed (`"*"`).  
- **Future**: we’ll restrict to:
  ```
  https://big‑site.dev, https://big‑site.com
  ```
  via the `CORS_ALLOW_ORIGINS` environment variable in Cloud Run.

---

## 4. Endpoint Cheat‑Sheet

| Method | Path       | Body                                      | Response                        |
|--------|------------|-------------------------------------------|---------------------------------|
| GET    | `/healthz` | —                                         | `{ "status": "ok" }`            |
| GET    | `/resume`  | —                                         | `{ "resume_text": "…" }`        |
| POST   | `/chat`    | `{ "question": "How do I…?" }`            | `{ "answer": "Sure, you can…"}` |

> All endpoints require the **Authorization** header with a valid Supabase JWT.

---

## 5. Example Calls

### cURL

```bash
curl -X POST https://<base_url>/chat   -H "Authorization: Bearer $JWT"   -H "Content-Type: application/json"   -d '{"question":"How can I optimize my capstone?"}'
```

### JavaScript (fetch)

```js
const jwt = supabase.auth.getSession().data.session.access_token;

const res = await fetch("https://<base_url>/chat", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${jwt}`,
  },
  body: JSON.stringify({ question: "How can I optimize my capstone?" })
});
const { answer } = await res.json();
```

---



Thank you!  
For any questions or support, reach out to the backend team.
