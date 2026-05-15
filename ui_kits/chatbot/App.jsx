const appStyles = {
  shell: {
    minHeight: "100dvh",
    display: "flex",
    flexDirection: "column",
    background: "var(--bg-canvas)",
    position: "relative",
  },
  ambient: {
    position: "fixed",
    inset: 0,
    pointerEvents: "none",
    backgroundImage:
      "radial-gradient(ellipse 60% 40% at 50% 0%, rgba(245,165,36,0.10) 0%, transparent 60%), " +
      "radial-gradient(ellipse 40% 30% at 90% 10%, rgba(230,57,70,0.06) 0%, transparent 70%)",
    zIndex: 0,
  },
  scroller: {
    flex: 1,
    overflowY: "auto",
    paddingTop: 16,
    paddingBottom: 16,
    position: "relative",
    zIndex: 1,
  },
  thread: { display: "flex", flexDirection: "column", gap: 12, maxWidth: 820, margin: "0 auto" },
  toBottom: {
    position: "absolute",
    right: 20,
    bottom: 12,
    width: 38,
    height: 38,
    borderRadius: "50%",
    background: "var(--bg-surface)",
    border: "1px solid var(--line)",
    boxShadow: "var(--e-2)",
    cursor: "pointer",
    color: "var(--ink-1)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 6,
  },
};

function App() {
  const [messages, setMessages] = React.useState([]);
  const [pending, setPending] = React.useState(false);
  const [showScrollBtn, setShowScrollBtn] = React.useState(false);
  const scrollerRef = React.useRef(null);
  const endRef = React.useRef(null);

  const send = (text) => {
    if (pending) return;
    const userMsg = { id: Date.now(), role: "user", text };
    setMessages((m) => [...m, userMsg]);
    setPending(true);

    // typing indicator
    setTimeout(() => {
      setMessages((m) => [...m, { id: "typing", role: "typing" }]);
    }, 240);

    // reply
    const reply = window.SS.findReply(text);
    setTimeout(() => {
      setMessages((m) =>
        m.filter((x) => x.id !== "typing").concat([
          {
            id: Date.now() + 1,
            role: "assistant",
            text: reply.text,
            kind: reply.kind,
            sources: reply.sources || [],
            products: reply.products || null,
          },
        ])
      );
      setPending(false);
    }, 900 + Math.min(700, text.length * 18));
  };

  const reset = () => {
    setMessages([]);
    setPending(false);
  };

  // Auto-scroll on new messages
  React.useEffect(() => {
    if (endRef.current) endRef.current.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  // Show "to bottom" button when scrolled up
  const onScroll = () => {
    const el = scrollerRef.current;
    if (!el) return;
    const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 80;
    setShowScrollBtn(!nearBottom);
  };

  const scrollToBottom = () => {
    if (endRef.current) endRef.current.scrollIntoView({ behavior: "smooth", block: "end" });
  };

  const { Header, Welcome, Message, Composer } = window;
  const { IconArrowDown } = window.SSIcons;
  const hasMessages = messages.length > 0;

  return (
    <div style={appStyles.shell}>
      <div style={appStyles.ambient} />
      <Header onReset={reset} hasMessages={hasMessages} />
      <div ref={scrollerRef} style={appStyles.scroller} onScroll={onScroll}>
        {!hasMessages && <Welcome onPick={send} />}
        <div style={appStyles.thread}>
          {messages.map((m) => (
            <Message key={m.id} msg={m} />
          ))}
          <div ref={endRef} />
        </div>
        {showScrollBtn && (
          <button
            style={appStyles.toBottom}
            onClick={scrollToBottom}
            aria-label="Scroll to latest"
          >
            <IconArrowDown size={16} strokeWidth={2} />
          </button>
        )}
      </div>
      <Composer onSend={send} showHints={hasMessages} />
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
