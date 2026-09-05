# Правила промптов на арты

Каждое правило оплачено испорченной картинкой. Не выкидывать при правке промптов руками.

## Обязательные строки

**Плоский лист, не свиток.**
```
FLAT sheet of aged cream parchment with softly ragged torn edges — NOT a rolled scroll, no curled corners
```
Без этого половина кадров рисуется свёрнутым свитком, и форма листа скачет между кадрами.

**Без рамки.**
```
NO drawn border, NO frame, NO ruled box — the drawing bleeds into bare parchment
```
Модель любит врисовать чёрную рамку внутрь листа.

**Никаких крестов.**
```
absolutely NOT a cross, no crucifix, no cross shape anywhere
```
Саренрэй — восьмилучевое солнце. По умолчанию вешается католический крест, особенно на чётках.

**Атрибут в одном месте.**
```
prayer beads in his hands ONLY — none around his neck, no second string
```
Приметный предмет модель дублирует: чётки окажутся и в руках, и на шее одновременно.

**Целая голова.**
```
The entire head is visible with generous margin above — do NOT crop the top of the head
```
В широком кадре бюст не помещается, и макушка срезается.

**Один персонаж.**
```
Single figure, no variant sheet, no multiple poses
```

## Композиция под 16:9

Генератор даёт широкий кадр, поэтому фигура ставится сбоку, а половина листа остаётся пустой:

```
COMPOSITION: the figure occupies roughly the left third of the wide frame, the rest is
bare stained parchment with ink splatters
```

Пустое поле не баг — туда ложится титр и оттуда начинается наезд камеры.

## Масштаб фигуры в интерьере

Генератор рисует фигуру отдельно и не сверяет её с обстановкой — выходит великан за детским столом. Помогают опорные сравнения, а не «сделай меньше»:

```
SCALE: the figure occupies about one third of the frame height. The tabletop reaches the
middle of his chest. The window behind him stays fully visible above his head.
```

## Позы

**Не просить движение — просить состояние.** «Садится», «подбегает», «вставая» дают либо прыжок, либо развал: модель рисует позу целиком и не умеет «на полпути».

Вместо этого: `SEATED AND COMPLETELY STILL, leaning forward from the waist, both forearms on the tabletop` — порыв несут корпус и взгляд, а поза статична.

Прямые запреты помогают: `NOT jumping, NOT airborne, NOT reclining, both feet on the floor`.

## Стиль — задавать явно каждый раз

После нескольких итераций генератор дрейфует в плоский контур. Стилевой блок писать в каждом промпте:

```
DRAWING STYLE: quick ink and light wash on aged cream parchment, confident dark brown pen
linework of varying weight, loose watercolour washes in muted earth tones, warm amber
pooling around the candle flame. NOT flat coloured lineart, NOT monochrome tint: the paper
must show real watercolour pooling and ink splatters.
```

## Разрежённость

Модель по умолчанию заполняет всё поле. Для полевого этюда нужна недосказанность:

```
Sparse and economical: large areas of bare paper left untouched, several shapes only
suggested and left unfinished, corners barely indicated
```

Но не перегибать: если убрать вместе с деталями и акварель, получится голый контур. Размывка должна работать как **свет** — пятна тепла там, где горит огонь, остальное бумага.

## Текст на картинке

Никогда не просить настоящих букв — генератор пишет латиницу, и это первое, по чему узнают ИИ-картинку. Кириллицу не умеет вовсе.

```
rows of writing rendered ONLY as loose wavering ink strokes — no letters, no words,
nothing readable
```

Титры накладываются в Resolve.

## Крупный план на пергаменте

Ловушка с двумя уровнями бумаги: наш стиль — рисунок **на** пергаменте, и если попросить нарисовать сам лист бумаги, уровни схлопываются и выходит фотография пергамента вместо рисунка.

Лечится тем, что в кадре оставляют кусок сцены:
```
the worn leather edge of the folder is still visible along one side, and a corner of the
desk shows beyond it
```

## Непрерывность

Проверять по раскадровке, что происходит в соседних кадрах. Пойманные ошибки первого выпуска:

- дверь была открыта в кадре, который идёт **до** того, как её открыли;
- ужин нарисован в таверне с посторонними людьми вместо дома на пятерых;
- вечер против утра — сверяться с архивом сессии, а не с памятью.
