# CLAUDE.md

Dit bestand bevat instructies voor Claude Code bij het werken aan dit project.

## Projectoverzicht

Dit project is een nieuwsaggregator-applicatie die automatisch nieuws ophaalt over de top-holdings van geselecteerde ETF's (Exchange Traded Funds). Het doel is om beleggers een snel overzicht te geven van relevante marktontwikkelingen rondom de bedrijven waarin zij via ETF's indirect beleggen.

## Kernfunctionaliteit

De applicatie moet de volgende kernfunctionaliteiten ondersteunen:

1. **ETF-beheer**: Een configureerbare lijst van ETF's (bijvoorbeeld VWRL, IWDA, QQQ, SPY) waarvoor nieuws moet worden verzameld.
2. **Holdings ophalen**: Per ETF de top-N holdings ophalen (standaard top 10), inclusief tickersymbool, bedrijfsnaam en weging in het fonds.
3. **Nieuws aggregeren**: Voor elk uniek bedrijf in de gecombineerde holdings recent nieuws ophalen via een nieuws-API.
4. **Deduplicatie**: Bedrijven die in meerdere ETF's voorkomen slechts één keer verwerken, maar wel tonen in welke ETF's ze zitten.
5. **Presentatie**: Een overzichtelijke weergave per bedrijf met de belangrijkste nieuwsberichten van de afgelopen 24-72 uur.

## Architectuur

Houd de volgende laagstructuur aan:

```
src/
├── etf/          # ETF-data en holdings ophalen
├── news/         # Nieuws-API integratie
├── aggregation/  # Samenvoegen en dedupliceren
├── storage/      # Caching van holdings en nieuwsartikelen
├── api/          # Backend endpoints (indien webapp)
└── ui/           # Frontend componenten (indien webapp)
```

Scheid de databron-integraties strikt van de bedrijfslogica zodat providers later vervangen kunnen worden zonder de rest van de codebase te raken.

## Externe databronnen

Voor ETF-holdings overweeg: ishares.com (officiële issuer-data), Yahoo Finance, of een betaalde provider zoals Financial Modeling Prep. Voor nieuws zijn NewsAPI, Finnhub, Alpha Vantage of de Marketaux API geschikte opties. Documenteer per bron de rate limits en of een API-sleutel nodig is.

API-sleutels horen **nooit** in de code of git-historie. Gebruik een `.env` bestand dat in `.gitignore` staat, en voeg een `.env.example` toe met dummy-waarden.

## Caching

Holdings van ETF's veranderen zelden (meestal kwartaal-rebalancing), dus cache deze minimaal 24 uur. Nieuwsberichten moeten korter gecacht worden, bijvoorbeeld 15-30 minuten, om actueel te blijven zonder onnodig API-quota te verbruiken. Implementeer caching expliciet en niet als bijzaak — het bepaalt direct of de applicatie schaalbaar en betaalbaar blijft.

## Tech-stack voorkeuren

Gebruik Python met FastAPI voor de backend en een lichte frontend (bijvoorbeeld React of een eenvoudige Jinja2-template). Voor data-handling: `httpx` voor async requests, `pydantic` voor modellen, en `pytest` voor tests. Vermijd zware frameworks tenzij ze duidelijk waarde toevoegen.

## Codestijl

Schrijf type-hints overal. Houd functies kort en met één duidelijke verantwoordelijkheid. Gebruik async waar I/O betrokken is — vooral bij het ophalen van nieuws voor tientallen bedrijven parallel. Geef foutmeldingen specifieke types (bijvoorbeeld `ETFNotFoundError`, `NewsAPIRateLimitError`) zodat ze hoger in de stack gericht afgehandeld kunnen worden.

## Tests

Elke externe API-integratie moet een mock-versie hebben voor tests. Schrijf integratietests voor de aggregatielogica met realistische voorbeelddata, vooral voor het deduplicatie-gedeelte — dat is waar bugs zich verstoppen.

## Disclaimer

De applicatie geeft géén beleggingsadvies. Voeg op elke pagina waar nieuws getoond wordt een duidelijke disclaimer toe dat de informatie puur informatief is.

## Wat te doen bij onduidelijkheid

Stel verduidelijkende vragen voordat je grote architecturale beslissingen neemt of nieuwe externe afhankelijkheden toevoegt. Vraag specifiek na: welke ETF's exact, welke nieuws-provider, en of dit een CLI-tool, webapp of API moet worden — deze keuzes bepalen veel downstream.
