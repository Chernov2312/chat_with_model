import React, { useEffect, useRef, useState } from "react";
import { apiRequest, streamMessage } from "./api.js";

const TOKEN_KEY = "chat-api-token";
const SESSION_KEY = "chat-api-session-id";

function readStored(key) {
  try {
    return localStorage.getItem(key) || "";
  } catch {
    return "";
  }
}

function App() {
  const [token, setToken] = useState(() => readStored(TOKEN_KEY));
  const [sessionId, setSessionId] = useState(() => readStored(SESSION_KEY));
  const [profile, setProfile] = useState(null);
  const [messages, setMessages] = useState([]);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isRegistering, setIsRegistering] = useState(false);
  const [newEmail, setNewEmail] = useState("");
  const [model, setModel] = useState("GigaChat-3-Ultra");
  const [systemPrompt, setSystemPrompt] = useState("Ты полезный ассистент.");
  const [temperature, setTemperature] = useState("0.7");
  const [maxTokens, setMaxTokens] = useState("2048");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const abortRef = useRef(null);

  useEffect(() => {
    if (token) {
      apiRequest("/api/v1/users/me", { token })
        .then((user) => {
          setProfile(user);
          setNewEmail(user.email || "");
        })
        .catch((cause) => setError(`Не удалось загрузить профиль: ${cause.message}`));
    } else {
      setProfile(null);
    }
  }, [token]);

  function rememberToken(value) {
    setToken(value || "");
    try {
      if (value) localStorage.setItem(TOKEN_KEY, value);
      else localStorage.removeItem(TOKEN_KEY);
    } catch (cause) {
      setError(`Не удалось сохранить токен в браузере: ${cause.message}`);
    }
  }

  function rememberSession(value) {
    setSessionId(value || "");
    try {
      if (value) localStorage.setItem(SESSION_KEY, value);
      else localStorage.removeItem(SESSION_KEY);
    } catch (cause) {
      setError(`Не удалось сохранить сессию в браузере: ${cause.message}`);
    }
  }

  async function runAction(action, successMessage) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const result = await action();
      if (successMessage) setNotice(successMessage);
      return result;
    } catch (cause) {
      setError(cause.message || "Неизвестная ошибка API.");
      return null;
    } finally {
      setBusy(false);
    }
  }

  async function login(event) {
    event.preventDefault();
    const result = await runAction(async () => {
      const form = new URLSearchParams({ username: email, password });
      return apiRequest("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: form,
      });
    });
    if (result?.access_token) rememberToken(result.access_token);
  }

  async function register(event) {
    event.preventDefault();
    const result = await runAction(
      () =>
        apiRequest("/api/v1/auth/register", {
          method: "POST",
          body: JSON.stringify({ username, email, password }),
        }),
      "Регистрация завершена.",
    );
    if (result?.access_token) rememberToken(result.access_token);
  }

  async function loadProfile() {
    const result = await runAction(() => apiRequest("/api/v1/users/me", { token }));
    if (result) {
      setProfile(result);
      setNewEmail(result.email || "");
    }
  }

  async function checkHealth() {
    const result = await runAction(() => apiRequest("/health"));
    if (result) setNotice(`API отвечает: ${result.status || "OK"}`);
  }

  async function updateProfile(event) {
    event.preventDefault();
    const result = await runAction(
      () =>
        apiRequest("/api/v1/users/me", {
          method: "PATCH",
          token,
          body: JSON.stringify({ email: newEmail }),
        }),
      "Профиль обновлён.",
    );
    if (result) setProfile(result);
  }

  async function createSession(event) {
    event.preventDefault();
    const result = await runAction(
      () =>
        apiRequest("/api/v1/sessions", {
          method: "POST",
          token,
          body: JSON.stringify({
            model,
            system_prompt: systemPrompt,
            temperature: Number(temperature),
            max_tokens: Number(maxTokens),
          }),
        }),
      "Чат создан.",
    );
    if (result?.id) {
      rememberSession(result.id);
      setMessages(Array.isArray(result.messages) ? result.messages : []);
    }
  }

  async function deleteSession() {
    if (!sessionId) return;
    const result = await runAction(
      async () => {
        await apiRequest(`/api/v1/sessions/${encodeURIComponent(sessionId)}`, { method: "DELETE", token });
        return true;
      },
      "Сессия удалена.",
    );
    if (result) {
      rememberSession("");
      setMessages([]);
    }
  }

  async function sendMessage(event) {
    event.preventDefault();
    const content = message.trim();
    if (!sessionId || !content || busy) return;
    setMessage("");
    setError("");
    setNotice("");
    setBusy(true);
    setMessages((items) => [...items, { role: "user", content }, { role: "assistant", content: "" }]);
    abortRef.current = new AbortController();
    try {
      for await (const eventData of streamMessage({
        sessionId,
        content,
        token,
        signal: abortRef.current.signal,
      })) {
        if (eventData.type === "token") {
          setMessages((items) => {
            const next = [...items];
            const last = next[next.length - 1];
            if (last?.role === "assistant") {
              next[next.length - 1] = { ...last, content: last.content + eventData.data };
            }
            return next;
          });
        } else if (eventData.type === "done") {
          setNotice("Ответ получен.");
        } else if (eventData.type === "error") {
          throw new Error(eventData.data);
        }
      }
    } catch (cause) {
      if (cause.name !== "AbortError") setError(cause.message || "Ошибка потока сообщений.");
    } finally {
      abortRef.current = null;
      setBusy(false);
    }
  }

  function logout() {
    rememberToken("");
    setProfile(null);
    setNotice("Токен удалён из браузера.");
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top"><span className="brand-mark">✳</span> dialog<span className="brand-muted">/</span>ai</a>
        <div className="topbar-right">
          <span className={`connection ${error ? "connection-error" : ""}`}>
            <i /> {error ? "Требуется внимание" : "API-клиент"}
          </span>
          {token && <button className="button button-quiet" onClick={logout}>Выйти</button>}
        </div>
      </header>

      <section className="hero" id="top">
        <div className="eyebrow"><span className="eyebrow-line" /> ЧАТ С МОДЕЛЬЮ <span className="eyebrow-dot">·</span> API V1</div>
        <h1>Идеи становятся<br /><span>диалогом.</span></h1>
        <p className="hero-copy">Минималистичный интерфейс для общения с AI.<br />Создайте сессию и начните с чистого листа.</p>
        <div className="hero-decoration decoration-one" />
        <div className="hero-decoration decoration-two" />
      </section>

      {(error || notice) && (
        <div className={`feedback ${error ? "feedback-error" : "feedback-success"}`} role="status">
          <span>{error ? "!" : "✓"}</span><p>{error || notice}</p>
          <button onClick={() => { setError(""); setNotice(""); }} aria-label="Закрыть сообщение">×</button>
        </div>
      )}

      <div className="workspace">
        <aside className="sidebar">
          <section className="panel auth-panel">
            <div className="section-heading"><span className="step">01</span><h2>Аккаунт</h2></div>
            {profile ? (
              <div className="profile-content">
                <div className="profile-badge">{(profile.email || "U").slice(0, 1).toUpperCase()}</div>
                <div className="profile-details"><strong>{profile.username}</strong><span>{profile.email}</span></div>
                <button className="icon-button" onClick={loadProfile} title="Обновить профиль">↻</button>
                <form className="stack-form full-width" onSubmit={updateProfile}>
                  <label htmlFor="update-email">Изменить email</label>
                  <div className="inline-input"><input id="update-email" type="email" required value={newEmail} onChange={(e) => setNewEmail(e.target.value)} /><button className="button button-small" disabled={busy}>Сохранить</button></div>
                </form>
              </div>
            ) : (
              <form className="stack-form" onSubmit={isRegistering ? register : login}>
                <p className="panel-hint">{isRegistering ? "Создайте аккаунт для защищённых операций." : "Войдите, чтобы пользоваться защищёнными операциями."}</p>
                {isRegistering && <>
                  <label htmlFor="username">Имя пользователя</label>
                  <input id="username" autoComplete="username" minLength="3" maxLength="50" required value={username} onChange={(e) => setUsername(e.target.value)} />
                </>}
                <label htmlFor="email">Email</label>
                <input id="email" type="email" autoComplete={isRegistering ? "email" : "username"} required placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} />
                <label htmlFor="password">Пароль</label>
                <input id="password" type="password" autoComplete={isRegistering ? "new-password" : "current-password"} minLength={isRegistering ? 8 : undefined} required value={password} onChange={(e) => setPassword(e.target.value)} />
                <button className="button button-primary button-wide" disabled={busy}>{isRegistering ? "Создать аккаунт" : "Войти"} <span>→</span></button>
                <button className="text-button" type="button" disabled={busy} onClick={() => setIsRegistering((value) => !value)}>{isRegistering ? "Уже есть аккаунт? Войти" : "Создать аккаунт"}</button>
              </form>
            )}
          </section>

          <section className="panel session-panel">
            <div className="section-heading"><span className="step">02</span><h2>Новый чат</h2></div>
            <form className="stack-form" onSubmit={createSession}>
              <label htmlFor="model">Модель</label>
              <input id="model" value={model} onChange={(e) => setModel(e.target.value)} required />
              <label htmlFor="prompt">Системный промпт</label>
              <textarea id="prompt" rows="3" value={systemPrompt} onChange={(e) => setSystemPrompt(e.target.value)} />
              <div className="two-fields">
                <div><label htmlFor="temperature">Температура</label><input id="temperature" type="number" min="0" max="2" step="0.1" value={temperature} onChange={(e) => setTemperature(e.target.value)} /></div>
                <div><label htmlFor="max-tokens">Макс. токенов</label><input id="max-tokens" type="number" min="1" value={maxTokens} onChange={(e) => setMaxTokens(e.target.value)} /></div>
              </div>
              <button className="button button-outline button-wide" disabled={busy}>＋ <span>Создать чат</span></button>
            </form>
            {sessionId && <button className="text-button danger-text" onClick={deleteSession} disabled={busy}>Удалить текущую сессию</button>}
          </section>

          <section className="panel profile-panel">
            <div className="section-heading"><span className="step">03</span><h2>Состояние</h2></div>
            <div className="status-row"><span>Авторизация</span><span className={token ? "status-value active" : "status-value"}><i />{token ? "Активна" : "Не выполнена"}</span></div>
            <div className="status-row"><span>Текущая сессия</span><span className="status-value">{sessionId ? "Подключена" : "Не выбрана"}</span></div>
            <div className="profile-actions"><button className="text-button" onClick={checkHealth} disabled={busy}>Проверить API</button></div>
            <div className="profile-actions">
              <button className="text-button" onClick={loadProfile} disabled={!token || busy}>Получить профиль</button>
              <a className="text-button" href={`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/docs`} target="_blank" rel="noreferrer">API Docs ↗</a>
            </div>
          </section>
        </aside>

        <section className="chat-panel">
          <div className="chat-header">
            <div><div className="chat-title"><span className="chat-title-mark">✳</span> Диалог <span className="live-dot" /></div><div className="chat-subtitle">{sessionId ? "Активный чат" : "Новая беседа"}</div></div>
            <div className="chat-meta"><span className="model-indicator" />{model}</div>
          </div>
          <div className="chat-body">
            {messages.length === 0 ? (
              <div className="empty-state">
                <div className="empty-orbit"><span>✳</span><i /><b /></div>
                <h3>С чего начнём?</h3>
                <p>Создайте сессию слева, чтобы начать диалог.<br />Ваш следующий вопрос может привести куда угодно.</p>
                <div className="suggestions">
                  {["Помоги придумать идею", "Объясни что-нибудь сложное", "Напиши небольшой рассказ"].map((item) => <button key={item} onClick={() => setMessage(item)}>{item}<span>↗</span></button>)}
                </div>
              </div>
            ) : (
              <div className="message-list">
                {messages.map((item, index) => (
                  <article className={`message-row ${item.role === "user" ? "message-user" : ""}`} key={item.id || index}>
                    <div className={`message-avatar ${item.role === "user" ? "user-avatar" : ""}`}>{item.role === "user" ? "Я" : "✳"}</div>
                    <div className="message-content"><div className="message-author">{item.role === "user" ? "Вы" : "Ассистент"}</div><p>{item.content}</p></div>
                  </article>
                ))}
                {busy && <div className="typing-indicator"><i /><i /><i /></div>}
              </div>
            )}
          </div>
          <form className="composer" onSubmit={sendMessage}>
            <textarea value={message} onChange={(e) => setMessage(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(e); } }} placeholder={sessionId ? "Напишите сообщение..." : "Сначала создайте или откройте сессию"} disabled={!sessionId || busy} rows="1" />
            <div className="composer-footer"><span><kbd>↵</kbd> отправить <span className="hint-divider">·</span> <kbd>⇧ ↵</kbd> новая строка</span><button className="send-button" type="submit" disabled={!sessionId || !message.trim() || busy} aria-label="Отправить">↑</button></div>
          </form>
          <div className="chat-footnote">Ответы AI могут быть неточными. Проверяйте важную информацию.</div>
        </section>
      </div>
      <footer className="page-footer"><span>СОЗДАНО ДЛЯ ЛЮБОПЫТНЫХ</span><span>CHAT WITH MODEL <b>·</b> 2026</span></footer>
    </main>
  );
}

export default App;
