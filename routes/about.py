from fasthtml.common import *

def register_about_routes(rt):
    @rt('/about')
    def about():
        return Html(
            Head(
                Meta(charset="UTF-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
                Meta(name="description", content="Informazioni sul progetto Sondaggi Nazionali. Metodologia e fonti utilizzate per l'analisi dei sondaggi politici italiani."),
                Meta(name="keywords", content="metodologia sondaggi, fonti sondaggi politici, about sondaggi nazionali"),
                Meta(name="robots", content="index, follow"),
                
                # Open Graph tags
                Meta(property="og:title", content="About | Sondaggi Nazionali"),
                Meta(property="og:description", content="Informazioni sul progetto Sondaggi Nazionali e la nostra metodologia."),
                Meta(property="og:image", content="https://sondagginazionali.it/static/og-image.png"),
                Meta(property="og:url", content="https://sondagginazionali.it/about"),
                Meta(property="og:type", content="website"),
                
                # Added canonical URL
                Link(rel="canonical", href="https://sondagginazionali.it/about"),
                
                Title("About | Sondaggi Nazionali"),
                Link(rel="icon", type="image/png", href="/static/favicon.png"),
                Link(rel="stylesheet", href="/static/styles.css"),
                Link(
                    rel="stylesheet",
                    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"
                ),
            ),
            Body(
                Header(
                    # Navbar
                    Div(
                        Div(
                            Div(
                                A("Expert Forecasting", href="/forecasting", cls="nav-link"),
                                cls="left-links"
                            ),
                            A("Sondaggi Nazionali", href="/", cls="nav-brand"),
                            Div(
                                A("About", href="/about", cls="nav-link"),
                                cls="right-links"
                            ),
                            cls="navbar-content"
                        ),
                        cls="navbar"
                    ),
                ),
                Main(
                    # Container with main content
                    Div(
                        # Main content
                        Div(
                            H1("About", cls="title"),
                            Div(
                                H2("Il Progetto", cls="section-title"),
                                P(
                                    """Sondaggi Nazionali è un progetto open source che raccoglie e analizza i sondaggi 
                                    politici italiani. Il progetto si basa su un altro mio strumento, """,
                                    A(
                                        "llm_italian_poll_scraper",
                                        href="https://github.com/ruggsea/llm_italian_poll_scraper",
                                        target="_blank",
                                        cls="inline-link"
                                    ),
                                    """, che estrae automaticamente i dati dal sito ufficiale del governo italiano, 
                                    dove per legge devono essere pubblicati tutti i sondaggi politici. L'obiettivo 
                                    è fornire una visione chiara e imparziale delle tendenze politiche in Italia 
                                    attraverso l'aggregazione di dati e previsioni riguardanti le elezioni politiche 
                                    italiane."""
                                ),
                                
                                H2("Metodologia", cls="section-title"),
                                P("""
                                    I dati vengono elaborati utilizzando una media mobile ponderata che dà più peso 
                                    ai sondaggi più recenti. Questo metodo permette di smorzare le fluttuazioni 
                                    casuali mantenendo la sensibilità ai cambiamenti reali nelle preferenze degli elettori.
                                """),
                                
                                H2("Contatti", cls="section-title"),
                                P("""
                                    Per domande, suggerimenti o segnalazioni, potete contattarmi attraverso i 
                                    seguenti canali:
                                """),
                                Div(
                                    A(
                                        I(cls="fab fa-twitter"), 
                                        "Twitter", 
                                        href="https://twitter.com/ruggsea", 
                                        target="_blank",
                                        cls="footer-link"
                                    ),
                                    A(
                                        I(cls="fab fa-linkedin"), 
                                        "LinkedIn", 
                                        href="https://www.linkedin.com/in/ruggsea/", 
                                        target="_blank",
                                        cls="footer-link"
                                    ),
                                    cls="contact-links"
                                ),
                                cls="about-content"
                            ),
                            Div(
                                A("← Torna alla home", href="/", cls="back-link"),
                                cls="navigation"
                            ),
                            cls="content"
                        ),
                        cls="container"
                    )
                ),
                Footer(
                    P("© 2024 Sondaggi Nazionali. Tutti i diritti riservati."),
                    cls="footer"
                )
            )
        ) 