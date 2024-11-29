from fasthtml.common import Html, Head, Body, Title, Link, Div, A, H1, H2, P, Script

def register_forecasting_routes(rt):
    @rt('/forecasting')
    def forecasting():
        return Html(
            Head(
                Title("Expert Forecasting"),
                Link(rel="icon", type="image/png", href="/static/favicon.png"),
                Link(rel="stylesheet", href="/static/styles.css"),
                Link(
                    rel="stylesheet",
                    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"
                ),
            ),
            Body(
                # External resources
                Link(rel="stylesheet", href="/static/styles.css"),
                
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
                
                # Container with main content
                Div(
                    Div(
                        H1("Expert Forecasting - Sondaggi Nazionali", cls="title"),
                        Div(
                            H2("Prediction Markets e Forecasting", cls="section-title"),
                            P("""
                                I prediction markets rappresentano uno strumento innovativo per prevedere eventi 
                                futuri, inclusi risultati politici. La letteratura accademica ha dimostrato 
                                ripetutamente la loro efficacia predittiva, spesso superando metodi tradizionali 
                                come i sondaggi.
                            """),
                            
                            P("""
                                Nonostante il loro potenziale, al momento non esistono mercati attivi sulle 
                                principali piattaforme di prediction markets (come Polymarket) per le elezioni 
                                italiane. Questa sezione è quindi un work in progress, che verrà aggiornata 
                                non appena saranno disponibili nuovi strumenti di previsione.
                            """),
                            
                            H2("Previsioni di Metaculus", cls="section-title"),
                            P("""
                                Nel frattempo, è possibile consultare le previsioni degli esperti su Metaculus, 
                                una piattaforma di forecasting che aggrega le previsioni di forecaster esperti:
                            """),
                            
                            # Metaculus embed using a div with innerHTML
                            Div(
                                Script("""
                                    document.currentScript.parentElement.innerHTML = `
                                        <iframe 
                                            src="https://www.metaculus.com/questions/embed/19630?theme=light&embedTitle=Which+party+will+win+the+most+seats+in+the+Chamber+of+Deputies+in+the+next+Italian+election%3F&zoom=all" 
                                            style="height:430px; width:100%; max-width:550px; border:none;"
                                        ></iframe>
                                    `;
                                """),
                                cls="metaculus-embed",
                                style="display: flex; justify-content: center; align-items: center; width: 100%; margin: 20px 0;"
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
            )
        ) 