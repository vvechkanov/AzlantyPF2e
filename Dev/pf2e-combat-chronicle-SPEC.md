# pf2e-combat-chronicle — Спецификация модуля

## Назначение

Foundry VTT модуль для PF2e, который автоматически протоколирует бои в структурированном формате (JSON + человекочитаемый журнал). Предназначен для:
1. **Пост-обработки боёв** — генерации нарративных пересказов и глав книги
2. **Тактического анализа** — понимания action economy, эффективности персонажей
3. **GM-рефлексии** — что работало, что нет, баланс энкаунтеров

## Среда

- **Foundry VTT:** v13+ (текущая: 13.351)
- **Система:** PF2e 7.11+
- **Только GM:** модуль работает на стороне GM, игрокам ничего не показывает
- **Без зависимостей:** не требует других модулей

---

## Что логируем

### 1. Структура боя (Combat Skeleton)

На каждый encounter автоматически фиксировать:

```
{
  encounter_id: string,
  scene_name: string,
  started_at: ISO timestamp,
  ended_at: ISO timestamp,
  initiative_order: [
    { name, actor_id, initiative_roll, initiative_total }
  ],
  rounds: [ ... ],
  summary: { ... }
}
```

**Хуки:** `combatStart`, `combatRound`, `deleteCombat` (или `combatEnd` если есть)

### 2. Раунды и ходы (Round/Turn tracking)

Для каждого раунда:
```
{
  round_number: number,
  turns: [
    {
      combatant_name: string,
      actor_id: string,
      turn_number: number,
      hp_start: number,
      hp_max: number,
      hp_end: number,         // фиксируется при окончании хода
      temp_hp_start: number,
      temp_hp_end: number,
      position_start: { x, y },
      position_end: { x, y },
      
      // === ПОЛНЫЙ СНАПШОТ ЭФФЕКТОВ (начало и конец хода) ===
      // Включает ВСЁ что висит на акторе как embedded items:
      // - conditions: Blinded, Prone, Frightened 2, Stunned, Sickened...
      // - spell effects: "Spell Effect: Lay on Hands", "Spell Effect: Evolution Surge"
      // - aura effects: "Aura: Angelic Halo", эманации, аура благословения
      // - buff/debuff effects: "Effect: Bless", "Effect: Rage", "Effect: Sanctuary"
      // - feat effects: "Effect: Rage Temp HP Immunity"
      // - item effects, toggle effects и т.д.
      //
      // Diff между start и end показывает что произошло за ход:
      // что получил, что потерял, что изменило value
      effects_start: [
        {
          name: string,          // "Ослеплён", "Aura: Angelic Halo", "Effect: Rage"
          type: string,          // "condition" | "effect" (PF2e item types)
          slug?: string,         // PF2e slug: "blinded", "angelic-halo"
          value?: number,        // для valued conditions: Frightened 2 → 2
          remaining_rounds?: number, // оставшаяся длительность в раундах (null = бессрочно)
          remaining_text?: string,   // "3 rounds", "1 minute", "until rest"
          source?: string        // кто/что наложило: "Калигни охотник", "Бель"
        }
      ],
      effects_end: [ /* та же структура */ ],
      
      // Автоматический diff (вычисляется из start vs end)
      effects_gained: string[],  // ["Effect: Rage", "Condition: Frightened 1"]
      effects_lost: string[],    // ["Ослеплён"]
      effects_changed: [         // изменение value
        { name: "Frightened", from: 2, to: 1 }
      ],
      
      actions: [ ... ],       // см. ниже
      chat_messages: [ ... ]  // ID или копии сообщений за этот ход
    }
  ]
}
```

**Хуки:** `combatTurn`, `updateActor` (для HP), `updateToken` (для позиции)

### 3. Действия (Action Tracking)

Самый сложный и ценный слой. На каждое действие в ходе:

```
{
  action_name: string,       // "Strike", "Cast a Spell", "Stride", "Rage" и т.д.
  action_cost: number,       // 1, 2, 3 или 0 (free/reaction)
  action_type: string,       // "strike", "spell", "skill", "move", "interact", "other"
  item_name?: string,        // название оружия/заклинания/предмета
  item_type?: string,        // "weapon", "spell", "feat", "consumable"
  targets?: string[],        // имена целей
  roll_result?: number,      // итог броска
  roll_formula?: string,     // формула броска "1d20 + 13"
  degree_of_success?: string,// "critical-success", "success", "failure", "critical-failure"
  damage_dealt?: number,     // нанесённый урон
  damage_type?: string,      // "slashing", "fire", "poison"
  healing_done?: number,     // исцеление
  map_penalty?: number,      // штраф MAP на момент атаки
  notes?: string             // доп. инфо (состояния, спецэффекты)
}
```

**Источники данных:**
- `createChatMessage` — главный хук; PF2e кладёт богатые данные в `message.flags.pf2e`:
  - `flags.pf2e.context` — тип действия, DC, модификаторы
  - `flags.pf2e.origin` — источник (item UUID, actor)
  - `flags.pf2e.modifiers` — список модификаторов с типами
  - `message.rolls` — массив Roll объектов с формулами и результатами
- `updateToken` — для отслеживания перемещений (дельта x/y → футы)
- Текст заклинания из `message.content` (но НЕ хранить весь HTML — только название)

### 4. HP-трекинг (Health Tracking)

На каждое изменение HP:
```
{
  actor_name: string,
  timestamp: ISO,
  hp_before: number,
  hp_after: number,
  hp_max: number,
  temp_hp_before: number,
  temp_hp_after: number,
  delta: number,             // отрицательное = урон, положительное = хил
  source?: string,           // кто нанёс урон / кто хилил (если известно)
  damage_type?: string
}
```

**Хуки:** `updateActor` (при изменении `system.attributes.hp`)

### 5. Эффекты и состояния (Effect & Condition Tracking)

Два механизма сбора:

#### 5a. Снапшоты на начало/конец хода (основной)
Полный снимок `actor.items.filter(i => i.type === "condition" || i.type === "effect")` — см. структуру `effects_start` / `effects_end` в секции 2.

Это даёт полную картину: на начало хода у Киран висели [Rage, Frightened 2], на конец — [Rage, Frightened 1]. Значит Frightened уменьшился. Для книги: «ярость помогала ей сдерживать страх».

#### 5b. Event-лог изменений (дополнительный)
Для точного понимания *когда именно* в ходе что произошло:

```
{
  actor_name: string,
  effect_name: string,       // "Ослеплён", "Aura: Angelic Halo", "Effect: Rage"
  effect_type: string,       // "condition" | "effect"
  slug?: string,
  event: "applied" | "removed" | "value_changed",
  old_value?: number,        // для value_changed
  new_value?: number,
  timestamp: ISO,
  round: number,
  turn: number,              // чей ход был активен
  source?: string            // кто/что наложило
}
```

**Что попадает в effects:**
- Conditions: Blinded, Prone, Frightened N, Stunned N, Sickened N, Unconscious...
- Spell Effects: "Spell Effect: Lay on Hands +2 AC", "Spell Effect: Evolution Surge"
- Aura Effects: "Aura: Angelic Halo" (бонус к хилу в радиусе)
- Buff/Debuff: "Effect: Bless", "Effect: Sanctuary", "Effect: Rage"
- Feat Effects: "Effect: Rage Temp HP Immunity"
- Toggle Effects: включаемые/выключаемые способности
- Временные эффекты от предметов

**Хуки:**
- `createItem` на актёре (type === "condition" || type === "effect") — эффект наложен
- `deleteItem` на актёре — эффект снят/истёк
- `updateItem` на актёре — изменение value (Frightened 2 → 1)

**Как это работает в PF2e:**
- `actor.items.filter(i => ["condition", "effect"].includes(i.type))` — все активные
- `item.name` — название эффекта
- `item.system.slug` — машинный идентификатор
- `item.system.value?.value` — числовое значение (для Frightened, Sickened)
- `item.system.duration` — длительность (rounds, minutes, unlimited)
- `item.system.context?.origin` — кто наложил

### 6. Перемещения (Movement Tracking)

```
{
  actor_name: string,
  from: { x, y },
  to: { x, y },
  distance_ft: number,       // рассчитать по grid settings сцены
  timestamp: ISO,
  round: number,
  turn: number
}
```

**Хуки:** `updateToken` (при изменении `x` или `y`)

---

## Вывод данных

### JSON-экспорт (основной)

- Полный JSON-файл для каждого encounter, сохраняемый как JournalEntry с флагом модуля
- Экспорт в файл по кнопке (скачать .json)
- Формат оптимизирован для парсинга (Claude / скрипты)

### Human-Readable журнал (вторичный)

Опциональная генерация читаемого текста в JournalEntry:

```
=== Encounter: Нападение калигни на дом Кинсуиков ===
Сцена: Гринфорд — дом Кинсуиков
Начало: 21.03.4726 (21:00 реального времени)
Длительность: 5 раундов

--- Инициатива ---
29 — Средний Гуманоид
28 — Керрен Тар-Крыло
25 — Бель
25 — Маленький Гуманоид ×2
22 — Калигни охотник ×2
...

--- Раунд 2 ---
[Киран] HP: 60/60 → 32/60 | Позиция: (14,8)→(16,10)
  Эффекты: — → [Rage, Frightened 1] (получила Rage, Frightened 2→1)
  1. Rage (1◆) — вход в ярость, +2 урон, temp HP 10
  2. Flurry of Blows (1◆) — удар по Маленькому Гуманоиду: 18 vs AC → попадание, 9 урон (дробящий)
  3. [получила урон] Калигни охотник: Двойной удар мечами → 28 урон (колющий)
  
[Самум] HP: 45/45 | Позиция: (10,6)→(12,8)
  Эффекты: [Kinetic Aura] → [Kinetic Aura] (без изменений)
  1. Stride (1◆) — перемещение 20 фт
  2. Tremor (2◆, overflow) — AoE 10ft burst, 3 цели, КС 19 Стойкость
     Маленький Гуманоид 1: провал, 3 урон
     Маленький Гуманоид 2: провал, 3 урон
     ...
```

### Сводка энкаунтера (Summary)

Автоматически рассчитывать после окончания боя. Чистый JS, без нейронок — это простая агрегация по структурированному JSON.

#### Базовая статистика
```
{
  total_rounds: number,
  total_damage_dealt: { [actor_name]: number },
  total_damage_taken: { [actor_name]: number },
  total_healing: { [actor_name]: number },
  kills: [ { killer, target, round } ],
  spells_cast: { [actor_name]: string[] },
  movement_total_ft: { [actor_name]: number }
}
```

#### Dice Stats (броски d20)
```
{
  per_actor: {
    [actor_name]: {
      total_d20_rolls: number,
      natural_20s: number,           // крит-саксессы по натуралке
      natural_1s: number,            // крит-фейлы по натуралке
      critical_successes: number,    // любые крит-саксессы (включая DC+10)
      critical_failures: number,     // любые крит-фейлы
      successes: number,
      failures: number,
      average_d20: number,           // средний бросок d20
      highest_roll: number,          // максимальный натуральный бросок
      lowest_roll: number,           // минимальный
      hit_rate: number,              // % попаданий атак (success + crit / total attacks)
    }
  }
}
```

#### Награды / Fun Facts (автоматические)

Генерируются из статистики, показываются игрокам после боя.
Каждая награда = { title, recipient, value, flavor_text }

**Боевые:**
- 🗡️ **Мясник** — больше всего урона за бой (total damage dealt)
- 🎯 **Снайпер** — лучший % попаданий (hit_rate, мин. 3 атаки)
- 💀 **Палач** — больше всего убийств (kills)
- 🛡️ **Танк** — больше всего урона принято и выжил
- 💚 **Целитель** — больше всего HP восстановлено
- ⚡ **Нова** — максимальный урон за один ход
- 🏃 **Марафонец** — больше всего перемещений (футы)

**Dice luck:**
- 🎲 **Баловень судьбы** — наивысший средний d20 за бой
- 💀 **Проклятый** — наименьший средний d20 за бой
- 🌟 **Крит-машина** — больше всего натуральных 20
- 😱 **Фумблер** — больше всего натуральных 1
- 📈 **Серия** — самая длинная серия попаданий подряд
- 📉 **Чёрная полоса** — самая длинная серия промахов подряд

**Тактические:**
- 🧙 **Заклинатель** — больше всего заклинаний за бой
- 🎭 **Мультитул** — использовал больше всего разных действий (уникальные action names)
- 🏰 **Стена** — меньше всего урона получено (среди PC)
- 🎪 **Дебаффер** — наложил больше всего состояний на врагов

**Особые (conditional):**
- 🔥 **One-shot** — убил врага с одного удара (только если произошло)
- 💀→💚 **Феникс** — упал до 0 HP и вернулся в бой (только если произошло)
- 🎯 **Первая кровь** — нанёс первый урон в бою
- 🏁 **Финишер** — нанёс последний урон, завершивший бой

#### Формат вывода наград

Два варианта:
1. **В JSON** — для парсинга и кастомных UI
2. **В человекочитаемый журнал** — красивый блок после сводки боя:

```
=== 🏆 Награды боя ===

🗡️ Мясник: Анканто (47 урона)
🎲 Баловень судьбы: Бель (средний d20: 14.3)
💀 Проклятый: Киран (средний d20: 8.7)
🌟 Крит-машина: Самум (3 натуральных 20)
💚 Целитель: Бель (31 HP восстановлено)
🛡️ Танк: Киран (28 урона принято)
🔥 One-shot: Гельдала — убила Маленького Гуманоида с одного удара!
```

#### Кампейн-трекинг (Phase 3+)

Аккумулировать награды через бои:
- Сколько раз каждый PC получал каждую награду
- Кампейн-лидерборд: всего урона, всего исцелений, всего критов
- Рекорды: максимальный урон за один удар за всю кампанию
- Средний d20 по всей кампании на игрока

Хранить в отдельном JournalEntry "Campaign Stats" или флаге модуля.

---

### Система ачивок (Phase 4)

Персистентные ачивки, которые PC зарабатывают через бои. Хранятся в кампейн-файле. Каждая ачивка может быть получена многократно — считается количество раз.

#### Принципы
- **Негативные ачивки — обязательны.** «Самый большой неудачник» — это весело, а не обидно. Стиль: ироничный, дружеский подкол.
- **Ачивки за конкретный бой** — выдаются после каждого энкаунтера, показываются сразу
- **Кампейн-ачивки** — разблокируются при достижении кумулятивных порогов (всего 100 урона, 10 криттов и т.д.)
- **Рекорд-ачивки** — фиксируют абсолютные рекорды кампании (макс урон за один удар, макс хил за один ход)
- Ачивка = `{ id, name, icon, description, type, recipient, value, encounter_id, timestamp }`

#### Бой-ачивки (выдаются после каждого боя)

**Урон и бой:**
- 🗡️ **«Мясорубка»** — больше всего урона за бой
- 🪓 **«Один удар»** — убил врага с одного удара
- ⚡ **«Нова»** — максимальный урон за один ход (среди всех PC)
- 🎯 **«Снайпер»** — лучший % попаданий (мин. 3 атаки)
- 💀 **«Палач»** — больше всего убитых врагов
- 🏁 **«Финишер»** — нанёс последний удар, завершивший бой
- 🩸 **«Первая кровь»** — нанёс первый урон в бою

**Исцеление и защита:**
- 💚 **«Святой целитель»** — больше всего HP восстановлено
- 🛡️ **«Живой щит»** — больше всего урона принял и выжил
- 🏰 **«Неприкасаемый»** — меньше всего урона получено (среди PC, участвовавших в бою)
- 💀→💚 **«Феникс»** — упал до 0 HP и вернулся в бой

**Кости (dice luck):**
- 🎲 **«Любимчик Дезны»** — наивысший средний d20 за бой
- 🌟 **«Крит-машина»** — больше всего натуральных 20
- 📈 **«В ударе»** — самая длинная серия попаданий подряд

**Негативные (позор и слава):**
- 💩 **«Рукожоп»** — наименьший % попаданий (мин. 3 атаки)
- 🤡 **«Любимчик Ламашту»** — наименьший средний d20 за бой
- 😱 **«Фумблёр»** — больше всего натуральных 1
- 📉 **«Чёрная полоса»** — самая длинная серия промахов подряд
- 🪦 **«Ванька-встанька»** — падал без сознания (каждое падение)
- 🤕 **«Мешок для битья»** — больше всего урона получено
- 🏃 **«Ноги-ноги-ноги»** — больше всего перемещений, меньше всего атак (бегал но не бил)
- 🧱 **«Стена, в которую попали»** — получил крит от врага
- 🎭 **«Зритель»** — сделал меньше всего действий за бой (не считая stunned/unconscious)

**Тактические:**
- 🧙 **«Книжный червь»** — больше всего заклинаний за бой
- 🎪 **«Мастер на все руки»** — использовал больше всего разных типов действий
- 🎭 **«Дебаффер»** — наложил больше всего состояний на врагов
- 🧹 **«Чистильщик»** — добил больше всего врагов, раненных другими

#### Кампейн-ачивки (кумулятивные пороги)

Разблокируются при достижении суммарного порога через все бои:

**Урон:**
- ⚔️ **«Сотня»** — суммарно нанёс 100 урона
- ⚔️ **«Тысячник»** — суммарно нанёс 1000 урона
- ⚔️ **«Легенда»** — суммарно нанёс 5000 урона

**Промахи и неудачи:**
- 🎯 **«Учусь попадать»** — промахнулся 50 раз суммарно
- 🎲 **«Кость меня ненавидит»** — выбросил натуральную 1 двадцать раз
- 🪦 **«Частый гость»** — упал без сознания 5 раз за кампанию
- 🪦 **«Постоянная прописка»** — упал без сознания 10 раз

**Исцеление:**
- 💚 **«Тысяча ОЗ»** — суммарно восстановил 1000 HP
- 💚 **«Ходячая аптека»** — хилил в каждом бою 5 боёв подряд

**Криты:**
- 🌟 **«Десяточка»** — 10 натуральных 20 за кампанию
- 🌟 **«Крит-лорд»** — 50 натуральных 20 за кампанию
- 😱 **«Полтинник позора»** — 50 натуральных 1 за кампанию

**Выживание:**
- 🛡️ **«Не убиваемый»** — пережил 5 боёв подряд без потери сознания
- 💀→💚 **«Феникс навсегда»** — вернулся из 0 HP пять раз за кампанию

#### Рекорд-ачивки (абсолютные рекорды кампании)

Выдаются при побитии текущего рекорда. Рекорд переходит к новому держателю:

- 🏆 **«Рекордный удар»** — максимальный урон за один удар за всю кампанию
- 🏆 **«Рекордный хил»** — максимальное исцеление за один каст
- 🏆 **«Рекордный крит»** — максимальный урон по криту
- 🏆 **«Рекордный невезунчик»** — наименьший суммарный d20 за один бой (мин. 5 бросков)
- 🏆 **«Рекордный везунчик»** — наивысший суммарный d20 за один бой (мин. 5 бросков)
- 🏆 **«Рекордная серия»** — максимальная серия попаданий подряд
- 🏆 **«Рекордный позор»** — максимальная серия промахов подряд

#### Хранение ачивок

```
{
  campaign_achievements: {
    [actor_id]: {
      achievements: [
        {
          id: "butcher",
          name: "Мясорубка",
          icon: "🗡️",
          times_earned: 3,
          first_earned: ISO timestamp,
          last_earned: ISO timestamp,
          encounters: ["enc_001", "enc_003", "enc_007"],
          best_value: 47     // для рекордных: лучшее значение
        }
      ],
      cumulative_stats: {
        total_damage_dealt: number,
        total_damage_taken: number,
        total_healing: number,
        total_kills: number,
        total_nat20s: number,
        total_nat1s: number,
        total_knockdowns: number,  // сколько раз падал в 0
        total_attacks: number,
        total_hits: number,
        total_misses: number,
        total_spells_cast: number,
        encounters_participated: number,
        longest_hit_streak: number,
        longest_miss_streak: number
      }
    }
  },
  campaign_records: {
    max_single_hit_damage: { actor, value, encounter_id, timestamp },
    max_single_heal: { actor, value, encounter_id, timestamp },
    max_crit_damage: { actor, value, encounter_id, timestamp },
    worst_luck_encounter: { actor, avg_d20, encounter_id },
    best_luck_encounter: { actor, avg_d20, encounter_id },
    longest_hit_streak: { actor, value, encounter_id },
    longest_miss_streak: { actor, value, encounter_id }
  }
}
```

Хранить в JournalEntry "Campaign Achievements" с флагом модуля. Обновлять после каждого боя.
```

---

## UI (минимальный)

- **Кнопка в Combat Tracker:** "📋 Export Chronicle" — выгружает JSON текущего или последнего боя
- **Настройки модуля:**
  - Вкл/выкл автосохранение в JournalEntry
  - Вкл/выкл human-readable журнал
  - Папка журнала (по умолчанию "Combat Chronicles")
- **Нет UI во время боя** — модуль работает тихо, не мешает игре

---

## Технические решения

### Хранение данных во время боя
- Хранить в `game.combatChronicle.currentEncounter` (в памяти)
- Не делать updateDocument на каждое действие — это тормозит
- Сбрасывать в JournalEntry только при окончании боя или по кнопке

### Привязка сообщений к ходам
- При `combatTurn` запоминать текущий combatant
- Все `createChatMessage` между двумя `combatTurn` относятся к текущему ходу
- Фильтровать по `message.speaker.actor` для точности

### PF2e-специфичные данные
- Степень успеха: `message.flags.pf2e.context.outcome`
- Тип действия: `message.flags.pf2e.context.type` (attack-roll, damage-roll, spell-attack-roll, saving-throw, skill-check)
- MAP: можно вычислить по `message.flags.pf2e.context.mapIncreases` или по порядку атак в ходе
- Условия: `actor.items.filter(i => i.type === "condition")`
- Эффекты: `actor.items.filter(i => i.type === "effect")` — баффы, ауры, spell effects
- Полный снапшот: `actor.items.filter(i => ["condition", "effect"].includes(i.type))`
- HP: `actor.system.attributes.hp.value` / `.max` / `.temp`

### Определение перемещений
- `updateToken` даёт дельту координат
- Расстояние в футах: `Math.abs(deltaX) + Math.abs(deltaY)` * `scene.grid.distance` (для grid-based)
- Или Euclidean: `Math.sqrt(dx² + dy²) * gridDistance`

### Edge cases
- Эйдолон + Призыватель: оба действуют в один ход через "Act Together" — логировать обоих на один turn
- Реакции: происходят вне хода — привязывать к тому, чей ход активен, с пометкой "reaction"
- Длительные эффекты: логировать только моменты применения/снятия
- Смерть / потеря сознания: специальная пометка при HP ≤ 0

---

## Модули-референсы

1. **Encounter Stats** (https://github.com/DrussLegend/encounter-stats) — подход к сбору статистики, JSON-экспорт, журнальные записи. НЕ совместим с v13.
2. **AI Combat Assistant PF2e** (https://github.com/cammoraton/foundryvtt-pf2e-ai-combat-assistant) — как они собирают combat state (HP, conditions, positioning, actions), парсинг PF2e flags.
3. **Damage Log** (https://github.com/cs96and/FoundryVTT-damage-log) — отслеживание HP-дельт. Архивирован, но подход к `updateActor` хук надёжный.

---

## Приоритеты реализации

### MVP (Phase 1)
- [ ] Структура боя: начало/конец, инициатива, раунды/ходы
- [ ] HP-трекинг на каждый ход (start/end)
- [ ] Снапшоты эффектов на начало/конец хода (effects_start, effects_end, diff)
- [ ] Логирование бросков атак и урона из ChatMessage
- [ ] JSON-экспорт в JournalEntry

### Phase 2
- [ ] Action classification (Strike, Spell, Skill, Move, etc.)
- [ ] Effect event-лог (точные моменты apply/remove/change)
- [ ] Movement tracking
- [ ] Human-readable журнал

### Phase 3
- [ ] UI: кнопка экспорта в Combat Tracker
- [ ] Настройки модуля
- [ ] Human-readable журнал

### Phase 4 — Статистика, награды и ачивки
- [ ] Encounter summary (базовая статистика: урон, хил, криты)
- [ ] Dice stats per actor (средний d20, hit rate, серии)
- [ ] Награды после боя (fun facts)
- [ ] Система ачивок (персистентные, кампейн-wide)
- [ ] Кампейн-лидерборд и рекорды

---

## Структура файлов модуля

```
pf2e-combat-chronicle/
├── module.json
├── scripts/
│   ├── module.js              # entry point, хук регистрация
│   ├── combat-tracker.js      # логика отслеживания раундов/ходов
│   ├── message-parser.js      # парсинг ChatMessage + PF2e flags
│   ├── health-tracker.js      # HP дельты
│   ├── movement-tracker.js    # позиции токенов
│   ├── effect-tracker.js      # эффекты + состояния (снапшоты + события)
│   ├── journal-writer.js      # запись в JournalEntry (JSON + текст)
│   └── utils.js               # хелперы
├── lang/
│   └── en.json
└── styles/
    └── chronicle.css          # минимальные стили для кнопки
```
