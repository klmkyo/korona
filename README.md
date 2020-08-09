# Wyniki.diag.pl Scraper
## Podsumowanie
Program na podstawie podanych mu danych:
- tworzy arkusz w Excelu zawierający dane pacjenta wraz z wynikami
- zapisuje plik PDF z wynikami

## Instalacja
- Sklonowanie repo:
```
    git clone https://github.com/klmkyo/korona
```
- Instalacja zależności
```
    pip install -r requirements.txt
```
## Użytkowanie
Skrypt przyjmuje 2 argumenty; \<plik txt do odczytania\> oraz \<plik csv do zapisania\>:
- plik do odczytania: zawiera on **kod kreskowy** oraz pierwsze **6 cyfer PESEL'u** niezbędne do zalogowania się na wyniki.diag.pl. Przykład formatowania widać w pliku ```dane.txt```
- plik do zapisania: program zapisze do niego **arkusz**, do którego będą dopisywani nowo sprawdzeni ludzie

Przykład użycia:
```
    python skrypt.py dane.txt tabela.csv
```

## Uwagi
- jeśli Excel zapyta się z jakim kodowaniem otworzyć plik, należy wybrać UTF-8
- jeśli podczas działania programu wystąpi błąd (np. z powodu utracenia internetu czy problemów ze strony wyników.diag /a zdarzają się często/) warto spróbować ponownie uruchomić skrypt
- nie należy przerywać działania skryptu, nawet jeśli nastąpi błąd, może to skutkować niepoprawnym działaniem programu

## Kontakt
W przypadku problemu z działaniem programu (co jest całkiem prawdopodobne) lub pytań zapraszam do pisania na **mklimek03@gmail.com**, postaram się jak najszybciej odpisać.