import { useEffect, useState } from "react";

export default function LoginModal({ isOpen, onClose }) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [demoMessage, setDemoMessage] = useState("");

    useEffect(() => {
        if (!isOpen) {
            return;
        }

        const handleEscape = (event) => {
            if (event.key === "Escape") {
                onClose();
            }
        };

        document.addEventListener("keydown", handleEscape);
        return () => document.removeEventListener("keydown", handleEscape);
    }, [isOpen, onClose]);

    if (!isOpen) {
        return null;
    }

    const showDemoNotice = (message) => {
        setDemoMessage(message);
        setPassword("");
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        showDemoNotice(
            "Sign-in is not connected yet. This screen is a UI preview only — no account was created and you are not logged in."
        );
    };

    return (
        <div
            className="login-overlay"
            role="presentation"
            onClick={onClose}
        >
            <div
                className="login-modal"
                role="dialog"
                aria-modal="true"
                aria-labelledby="login-title"
                onClick={(event) => event.stopPropagation()}
            >
                <button
                    type="button"
                    className="login-close"
                    aria-label="Close sign in"
                    onClick={onClose}
                >
                    ×
                </button>

                <p className="login-eyebrow">✦ ForkAI account</p>
                <h2 id="login-title">Welcome back</h2>
                <p className="login-subtitle">
                    Sign in to ForkAI to save restaurants and personalize
                    your experience.
                </p>

                <form className="login-form" onSubmit={handleSubmit}>
                    <label className="login-label" htmlFor="login-email">
                        Email
                    </label>
                    <input
                        id="login-email"
                        type="email"
                        autoComplete="email"
                        placeholder="you@example.com"
                        value={email}
                        onChange={(event) => setEmail(event.target.value)}
                    />

                    <label className="login-label" htmlFor="login-password">
                        Password
                    </label>
                    <input
                        id="login-password"
                        type="password"
                        autoComplete="current-password"
                        placeholder="Enter your password"
                        value={password}
                        onChange={(event) => setPassword(event.target.value)}
                    />

                    <button type="submit" className="login-submit">
                        Sign in
                    </button>
                </form>

                {demoMessage ? (
                    <p className="login-demo-notice" role="status">
                        {demoMessage}
                    </p>
                ) : null}

                <p className="login-footer">
                    Don&apos;t have an account?{" "}
                    <button
                        type="button"
                        className="login-link-button"
                        onClick={() =>
                            showDemoNotice(
                                "Sign-up is not available yet. Authentication will be added in a future version."
                            )
                        }
                    >
                        Sign up
                    </button>
                </p>
            </div>
        </div>
    );
}
