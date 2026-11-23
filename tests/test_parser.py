from tools.parser import extract_text


def test_extract_text_removes_noise():
    html = """
    <html>
        <head>
            <style>body { color: red; }</style>
            <script>alert("hello");</script>
        </head>
        <body>
            <header>Site Header</header>
            <nav>Navigation</nav>
            <main>
                <h1>API Authentication</h1>
                <p>OAuth 2.0 is supported.</p>
            </main>
            <footer>Site Footer</footer>
        </body>
    </html>
    """

    text = extract_text(html)

    assert "API Authentication" in text
    assert "OAuth 2.0 is supported." in text
    assert "alert" not in text
    assert "Navigation" not in text
    assert "Site Footer" not in text