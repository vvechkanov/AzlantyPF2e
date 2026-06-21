# Азланти — Хаб

> Граф арки 2 (Абсалом). Сверху обзор всех больших сущностей и связей. Ниже — раскрытие каждой по отдельности.

---

## 🗺️ Обзор

```d2
direction: right

Sources: "Входные нити" {
  style.fill: "#fdf6e3"
  style.font-size: 22
  style.bold: true

  Tosha: "Учёный-старик\n(для Самума)"
  Bell: "Попаданка Бель"
  Varen: "Варен (для Анканто)"
  Tarven: "Тарвен (для Анканто)"
  Anchanto: "История Анканто"
  Kiran: "Статуэтка Ирори"
}

Doris: "Энис Салар" {
  shape: hexagon
  style.fill: "#fff3b0"
  style.font-size: 22
  style.bold: true
}

HouseOrmuz: "Дом Ормуз" {
  style.fill: "#e8f1fb"
  style.font-size: 26
  style.bold: true
}
HouseBlakros: "Дом Блакрос" {
  style.fill: "#e8f1fb"
  style.font-size: 26
  style.bold: true
}
HouseDamak: "Дом Дамак" {
  style.fill: "#e8f1fb"
  style.font-size: 26
  style.bold: true
}
Arcanamirium: "Арканамириум" {
  style.fill: "#efe6f7"
  style.font-size: 26
  style.bold: true
}
Pathfinders: "Pathfinder Society" {
  style.fill: "#efe6f7"
  style.font-size: 26
  style.bold: true
}
Syrvas: "Круг Syrvas" {
  style.fill: "#fde8e8"
  style.font-size: 28
  style.bold: true
}

Sources.Tosha -> Arcanamirium
Sources.Bell -> Arcanamirium
Sources.Varen -> Doris
Sources.Tarven -> Pathfinders
Sources.Anchanto -> Doris: природа меча
Sources.Kiran -> HouseOrmuz: "?"
Doris -> HouseOrmuz: "учёные / артифайсеры"

HouseOrmuz -> Syrvas: донор {style.stroke-dash: 5}
HouseDamak -> Syrvas: донор {style.stroke-dash: 5}
```

---

## 🏛️ Дом Ормуз

```d2
direction: down

Ormuz: "Дом Ормуз" {
  style.fill: "#e8f1fb"
  style.font-size: 30
  style.bold: true

  Yamtar: "Лорд Ямтар\nмеценат / салоны"
  Kaisar: "Кайсар\nдолговая расписка 50 зм"
  Yamtar -- Kaisar
}

Elarion: "Эларион Меретис\n(из Круга Syrvas)" {
  style.fill: "#fde8e8"
}
Elarion -- Ormuz.Yamtar: "советник (скрыто)" {
  style.stroke-dash: 5
}
```

---

## 🏛️ Дом Блакрос

```d2
direction: down

Blakros: "Дом Блакрос" {
  style.fill: "#e8f1fb"
  style.font-size: 30
  style.bold: true

  Head: "Глава (TBA)"
  Note: "хорошо платит, без вопросов"
  Risk: "конкуренты начнут искать\nутечка ~50%"
  Head -- Note
  Head -- Risk
}
```

---

## 🏛️ Дом Дамак

```d2
direction: down

Damak: "Дом Дамак" {
  style.fill: "#e8f1fb"
  style.font-size: 30
  style.bold: true

  Head: "Глава (TBA)"
  Money: деньги
  Logistics: логистика
  Head -- Money
  Head -- Logistics
}

Syrvas: "Круг Syrvas" {
  style.fill: "#fde8e8"
  style.font-size: 22
}

Damak -> Syrvas: "донор (скрыто)" {
  style.stroke-dash: 5
}
```

---

## 📚 Арканамириум

```d2
direction: down

Arcanamirium: "Арканамириум" {
  style.fill: "#efe6f7"
  style.font-size: 30
  style.bold: true

  Library: Библиотека
  RelicStudies: "Кафедра Relic Studies\n(специалисты по\nазлантийским артефактам)"
  Risk: "экспертиза: риск\nконфискации ~20%"
  Library -- RelicStudies
  RelicStudies -- Risk
}
```

---

## 🗺️ Pathfinder Society

```d2
direction: down

Pathfinders: "Pathfinder Society" {
  style.fill: "#efe6f7"
  style.font-size: 30
  style.bold: true

  Lodge: "Ложа\nForeign Quarter"
  Contact: "Контакт-приёмщик\n(TBA)"
  Buy: "~500 зм за пульт\nрепутация / расспросы"
  Lodge -- Contact
  Contact -- Buy
}
```

---

## 🔴 Круг Syrvas — Семёрка (для ГМа)

```d2
direction: down

Syrvas: "Круг Syrvas — Семёрка" {
  style.fill: "#fde8e8"
  style.font-size: 32
  style.bold: true

  Valastir: "Валастир Каэрваль\n(глава)"
  Yoren: "Йорен Орувиэль\nсвязной с Хоуп"
  Elarion: "Эларион Меретис\nпри Ямтаре (Ормуз)"
  Saviya: "Савийя Талорин\nстрогий учитель"
  Maelis: "Маэлис Сот-Ану\nзащитница"
  Doren: "Дорен Виракон\nщит в поле"
  Lisera: "Лисера Кетхарин\nрешительность"

  Valastir -- Yoren
  Valastir -- Elarion
  Valastir -- Saviya
  Valastir -- Maelis
  Valastir -- Doren
  Valastir -- Lisera
  Elarion -> Yoren: наставник
}

Yamtar: "Лорд Ямтар\n(Дом Ормуз)" {
  style.fill: "#e8f1fb"
}
Hope: "Хоуп\n(приют, Лужи)" {
  style.fill: "#fff3b0"
}

Syrvas.Elarion -> Yamtar: советник {style.stroke-dash: 5}
Syrvas.Yoren -> Hope: связной {style.stroke-dash: 5}
```

---

## Легенда

- **Сплошные стрелки** — открытые сюжетные нити, что партия видит.
- **Пунктир** — связи Круга Syrvas, скрытые от партии до уровня 7–9.
- **Шестиугольник (Энис Салар)** — социальный мост.
- **Голубые контейнеры** — дворянские дома.
- **Фиолетовые** — академические/исследовательские.
- **Розовый** — Круг Syrvas.
- **Бежевые** — источники нитей.
