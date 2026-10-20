# Creatio Demo Scriptwriter — installation and first run

About 5 minutes, once per computer. What the agent does: [CAPABILITIES.md](CAPABILITIES.md).

## 1. What you need

| | Required? | How to check / get it |
|---|---|---|
| **Claude Code** — the Claude desktop app (Code tab) or the Claude Code CLI | required | you already use it if you use other Creatio plugins |
| **Python 3.10 or newer** | required | run `python --version` in a terminal; if missing or older, install from [python.org](https://www.python.org/downloads/) and tick *Add python.exe to PATH*. The agent installs its own Python libraries on the first run. |
| **Microsoft Word** (or LibreOffice) | recommended | lets the agent render the documents and check how they look before handing them over |
| **Microsoft 365 connector** in claude.ai | recommended | claude.ai → **Settings → Connectors** → Microsoft 365 → connect with your Creatio account. Lets the agent search past demos and battlecards in SharePoint. Without it the script is still written, and the skipped research is listed as a research gap. |

## 2. Install

In any Claude Code chat, run these two commands, one after the other:

```
/plugin marketplace add VitaliiaKovalenko/creatio-demo-scriptwriter
```

```
/plugin install creatio-demo-scriptwriter@creatio-demo-scriptwriter
```

**Desktop app alternative:** **+** → **Plugins** → **Add plugin** → paste `VitaliiaKovalenko/creatio-demo-scriptwriter` →
install *creatio-demo-scriptwriter*.

Then **start a new chat** — plugins load when a chat starts.

## 3. Check it works

In the new chat, type `/demo` — the command **/creatio-demo-scriptwriter:creatio-demo-script-generator** should appear
in the suggestions. That's it.

## 4. Your first script

1. Open a **new chat** for each new customer (keeps one customer's material from mixing with another's).
2. Either type `/demo` and pick the command, **or** simply ask in plain words — for example:
   > Write a demo script for Alpine Dairy. Use cases: … Here's the discovery call transcript: … ARR is about $120k.

   A clear request for a demo script starts the agent on its own; the command just guarantees it.
3. Paste the discovery-call transcript and attach the customer's documents (or give the folder path).
4. Answer the few questions it asks (the **deal ARR** is always one of them).
5. Wait 20–30 minutes. The result lands in a `<Customer>_demo_script` folder in your working folder.
6. Revise in the same chat in plain words — no command needed: *"accept PA1 and PA3, reject PA2"*,
   *"UC2 step 4 — a button, not a list"*.

## 5. Updates

When a new version is announced:

```
/plugin marketplace update creatio-demo-scriptwriter
```

Then start a new chat.

## 6. Troubleshooting

| Symptom | Fix |
|---|---|
| `/demo` shows nothing after installing | Start a new chat. Still nothing: run `/plugin`, open **Manage plugins**, check *creatio-demo-scriptwriter* is enabled. |
| "Python is missing or too old" | Install Python 3.10+ from python.org (tick *Add to PATH*), restart the Claude app, try again. |
| "pip install failed" | Run the command it prints yourself in a terminal (corporate proxies sometimes block the automatic install). |
| Documents are written but "could not render" | Word or LibreOffice is missing — the files are fine; only the agent's visual self-check was skipped. |
| Script says *SharePoint search unavailable* under research gaps | Connect the Microsoft 365 connector in claude.ai (Settings → Connectors) and start a new chat. |
| The agent appears twice | You have a personal copy too (in `~/.claude/agents` / `~/.claude/skills`); remove one of them. |

## 7. Uninstall

```
/plugin uninstall creatio-demo-scriptwriter@creatio-demo-scriptwriter
```
