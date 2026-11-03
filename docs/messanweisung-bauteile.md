# Messanweisung Bauteile AES17-Filter

Stand: 3. November 2026

## Worum es geht

Ihr messt 106 Bauteile und stellt daraus passende Paare für fünf Filterplatinen zusammen. Der Filter hat zwei gleich aufgebaute Zweige, ein Plus- und einen Minus-Zweig. Er funktioniert nur dann gut, wenn sich die Bauteile beider Zweige möglichst genau gleichen.

Das absolute Ergebnis ist dabei weniger wichtig als der Vergleich: Es zählt, wie gut zwei Bauteile zueinander passen. Deshalb müssen alle Teile einer Sorte unter genau gleichen Bedingungen gemessen werden.

Am Ende gebt ihr drei Dinge ab: die Messtabelle, die Paarliste und die beschrifteten Beutel.

## Bauteile und Sollwerte

Von jeder Sorte ist mehr da, als gebraucht wird. So lassen sich gute Paare finden, der Rest bleibt übrig.

| Bauteil | Typ | Vorhanden | Gebraucht | Sollwert | Erlaubter Bereich |
| --- | --- | --- | --- | --- | --- |
| Spule | Würth 7687480102 | 40 | 20 | 1 mH ±5 % | 0,950 bis 1,050 mH |
| Kondensator 4,7 nF | WIMA FKP2, 630 V | 26 | 20 | 4,7 nF ±2,5 % | 4,583 bis 4,818 nF |
| Kondensator 220 pF | WIMA FKP2, 630 V | 40 | 30 | 220 pF ±2,5 % | 214,5 bis 225,5 pF |

Ein Teil außerhalb des Bereichs wird trotzdem eingetragen und in der Tabelle markiert. Es kommt in einen eigenen Beutel. Liegen viele Teile außerhalb, stimmt wahrscheinlich etwas am Messaufbau: dann anhalten und nachfragen.

## Vorbereitung und Messgerät

Gemessen wird mit einem LCR-Meter, das mindestens vier Stellen anzeigt. Ein einfaches Multimeter reicht nicht. Stellt das Gerät so ein und lasst es für eine ganze Bauteilsorte unverändert:

| Bauteil | Messart | Frequenz | Nachfragen, wenn |
| --- | --- | --- | --- |
| Spule | Ls (Serie) | 1 kHz | Anzeige schwankt um mehr als 0,2 % |
| Kondensator 4,7 nF | Cp (parallel) | 1 kHz | Anzeige schwankt um mehr als 0,2 % |
| Kondensator 220 pF | Cp (parallel) | 10 kHz, sonst 1 kHz | Anzeige schwankt um mehr als 0,5 pF |

Die Messspannung bleibt auf der kleinsten Standardeinstellung, ohne Gleichspannungsvorspannung. Schreibt Gerät, Frequenz und Messspannung oben in die Tabelle.

1. Gerät mindestens 30 Minuten vorher einschalten.
2. Bauteile mindestens eine Stunde im Messraum liegen lassen, damit sie Raumtemperatur haben.
3. Messadapter anschließen und Offen- und Kurzschlusskompensation durchführen.
4. Kompensation nach jedem Wechsel des Adapters wiederholen.

**Damit alle Werte vergleichbar bleiben:**

- Eine Bauteilsorte in einem Durchgang messen, mit demselben Gerät und Adapter.
- Bauteile nicht lange in der Hand halten, Handwärme verfälscht den Wert. Mit Pinzette oder kurz an den Anschlüssen greifen.
- Während der Messung die Finger vom Bauteil nehmen.
- Jedes Bauteil gleich tief und an gleicher Stelle im Adapter einsetzen.
- Besonders bei 220 pF: Adapter und Kabel nicht bewegen, schon die Lage verändert den Wert.

## Messen

Jedes Bauteil bekommt eine eigene Nummer, damit es nach dem Messen eindeutig bleibt.

| Bauteil | Nummern |
| --- | --- |
| Spulen | L01 bis L40 |
| Kondensatoren 4,7 nF | G01 bis G26 |
| Kondensatoren 220 pF | K01 bis K40 |

1. Bauteile der Reihe nach in ein Stück Styropor oder Pappe stecken und die Nummer daneben schreiben. Die Anschlussdrähte dabei nicht knicken.
2. Jedes Bauteil einsetzen, warten, bis die Anzeige ruhig ist, und den Wert mit allen angezeigten Stellen eintragen.
3. Nach je zehn Bauteilen das erste Bauteil der Sorte noch einmal messen. Weicht es um mehr als 0,2 % ab, die letzten zehn Teile wiederholen.
4. Am Ende fünf zufällige Teile erneut messen und beide Werte notieren.

Die Tabelle sieht für jede Sorte so aus, die Werte sind nur Beispiele. In Excel genügt je Sorte ein Blatt, das nach dem Messwert sortiert werden kann.

| Nummer | Messwert | Einheit | Bemerkung | Paar |
| --- | --- | --- | --- | --- |
| L01 | 1,0034 | mH |  |  |
| L02 | 0,9871 | mH |  |  |

## Paare bilden

Sortiert jede Tabelle nach dem Messwert: Nebeneinanderliegende Teile passen am besten zusammen. Die Abweichung eines Paars rechnet ihr so aus:

Abweichung in % = (größerer Wert − kleinerer Wert) / kleinerer Wert × 100

Die Platinen heißen A bis E. Auf jede Platine kommen diese Gruppen:

| Bauteil | Gruppen pro Platine | Gesamt | Ziel | Grenze |
| --- | --- | --- | --- | --- |
| Spulen | L1/L3 und L2/L4 | 10 Paare | bis 1 % | 1 % |
| 4,7 nF | C3/C7 und C4/C8 | 10 Paare | bis 1 % | 1 % |
| 220 pF, einzeln | C1/C5 | 5 Paare | bis 1 % | 2 % |
| 220 pF, als Summe | C2 + C9 gegen C6 + C10 | 5 Vierergruppen | bis 1 % | 2 % |

**Spulen und 4,7 nF:** Sucht die zehn Paare mit der kleinsten Abweichung. Welches Paar auf welche Platine kommt, ist egal.

**220 pF:**

1. Sucht die fünf Paare mit der kleinsten Abweichung. Das sind die Paare für C1/C5.
2. Nehmt aus dem Rest je vier Teile mit ähnlichen Werten.
3. Teilt die vier in zwei Zweiergruppen, sodass beide Summen fast gleich sind: das kleinste mit dem größten Teil gegen die beiden mittleren.
4. Rechnet die Abweichung mit den beiden Summen aus.

Lässt sich eine Grenze nicht einhalten, tragt das beste mögliche Paar ein und markiert es. Tauscht keine Messwerte aus und rundet nichts schön.

Die Paarliste sieht so aus:

| Platine | Position | Teile | Messwerte | Abweichung in % |
| --- | --- | --- | --- | --- |
| A | L1/L3 |  |  |  |
| A | L2/L4 |  |  |  |
| A | C3/C7 |  |  |  |
| A | C4/C8 |  |  |  |
| A | C1/C5 |  |  |  |
| A | C2 + C9 / C6 + C10 |  |  |  |

Dieselben sechs Zeilen gibt es für die Platinen B bis E.

## Wickelsinn der Spulen

Bei den 20 ausgewählten Spulen markiert ihr nach dem Paaren denselben Anschluss, weil der Hersteller den Wicklungsanfang nicht kennzeichnet. So lassen sich alle Spulen gleich herum einlöten, und Störfelder heben sich zwischen den Zweigen auf.

Ihr braucht einen Funktionsgenerator, ein Zweikanal-Oszilloskop, einen Widerstand 100 Ω und eine übrige Spule als Sendespule.

1. Generator auf Sinus, 1 kHz, etwa 1 V einstellen.
2. Generator über den 100-Ω-Widerstand an die Sendespule anschließen. Das andere Ende der Sendespule geht an die Generatormasse.
3. Kanal 1 an den Generatorausgang legen, vor dem Widerstand.
4. Sendespule fest auf den Tisch stellen und nicht mehr bewegen.
5. Prüfspule mit den Anschlüssen nach oben mittig auf die Sendespule stellen.
6. Einen Anschluss der Prüfspule an die Tastspitze von Kanal 2 legen, den anderen an die Masseklemme.
7. Die Phasenlage zwischen Kanal 1 und Kanal 2 ablesen. Sie liegt ungefähr bei +90° oder −90°. Ist das Signal zu klein, Mittelung einschalten oder die Spannung auf bis zu 5 V erhöhen.
8. Bei −90° die beiden Anschlüsse tauschen. Bei +90° den Anschluss an der Tastspitze mit einem Lackpunkt markieren.
9. Alle 20 Spulen in derselben Lage so prüfen, zum Schluss die erste noch einmal als Kontrolle.

Die Spulen dürfen dabei nicht gequetscht werden. Tragt in der Tabelle bei jeder Spule ein, dass sie markiert ist.

## Abgabe

Jede Gruppe aus der Paarliste kommt in einen eigenen kleinen Beutel, beschriftet mit Platine, Position und Nummern, zum Beispiel „A, L1/L3, L12 und L13“.

- [ ] Messtabellen für alle drei Sorten mit Gerät, Frequenz und Messspannung
- [ ] Ergebnisse der Kontrollmessungen
- [ ] Paarliste für die Platinen A bis E
- [ ] 30 beschriftete Beutel, je sechs pro Platine
- [ ] 20 Spulen mit Lackpunkt
- [ ] Ein Beutel „Rest“ und, falls nötig, ein Beutel „außerhalb des Bereichs“

**Bitte nicht:** Anschlussdrähte kürzen, knicken oder verlöten, Bauteile aus ihren Beuteln mischen, oder Werte nachträglich glattziehen. Bei Unklarheiten lieber kurz nachfragen.
