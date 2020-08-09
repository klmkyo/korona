# Wyniki.diag.pl Scraper
Program na podstawie podanych mu danych:
- tworzy arkusz w Excelu zawierający dane pacjenta wraz z wynikami
- zapisuje plik PDF z wynikami

*Testowany na Windowsie 10 oraz Linux'ie*

## Instalacja
- Sklonowanie repo:
```
    git clone https://github.com/klmkyo/korona
```
- Instalacja zależności (na Windowsie może być konieczne instalowanie z poziomu Administratora)
```
    pip install -r requirements.txt
```
- Instalacja Webdriver'a dla Firefoxa (niezbędny do interfejsowania z przeglądarką, z Chromem występowały problemy), rozpakowany plik należy skopiować do folderu ze skryptem:
```
    https://github.com/mozilla/geckodriver/releases
```

## Użytkowanie
Skrypt przyjmuje 2 argumenty; **\<plik txt do odczytania\>** oraz **\<plik csv do zapisania\>**:
- plik do odczytania: zawiera on **kod kreskowy** oraz pierwsze **6 cyfer PESEL'u** niezbędne do zalogowania się na wyniki.diag.pl. Przykład formatowania widać w pliku ```dane.txt```
- plik do zapisania: program zapisze do niego **arkusz**, do którego będą dopisywani nowo sprawdzeni ludzie

Przykład użycia:
```
    python script.py dane.txt tabela.csv
```

## Uwagi
- jeśli skrpyt ma problem z pobraniem pliku należy zwiększyć okno przeglądarki (aby wyjść z widoku mobilnego, który powoduje problemy)
- jeśli Excel zapyta się z jakim kodowaniem otworzyć plik, należy wybrać UTF-8
- nie należy przerywać działania skryptu, nawet jeśli nastąpi błąd, może to skutkować niepoprawnym działaniem programu
- jeśli podczas działania programu wystąpi błąd (np. z powodu utracenia internetu czy problemów ze strony wyników.diag */a zdarzają się często/*) warto spróbować ponownie uruchomić skrypt

## Kontakt
W przypadku problemu z działaniem programu (co jest całkiem prawdopodobne) lub pytań zapraszam do pisania na **mklimek03@gmail.com**, z chęcią udzielę pomocy.