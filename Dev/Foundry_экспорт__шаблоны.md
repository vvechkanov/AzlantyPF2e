# Foundry-экспорт: шаблоны актёров и сцен

Версии мира: core **13.351**, system **pf2e 7.11.2**, worldId **kampejn-a**.
Файлы кладём в `C:\Users\vechk\Desktop\AZL_S20\` (`actors/`, `scenes/`, `art/`) — **не в Downloads**.
Влад импортирует руками через Foundry UI.

## Актёр (NPC)

Эталон: `fvtt-Actor-kaspar-«ogarok»-5Tq6i2kNf4xIXXZT.json` (реcкин `Mage for Hire` из Pathfinder NPC Core).

Имя файла: `fvtt-Actor-{slug}-{_id}.json`, `_id` — случайные 16 символов `[A-Za-z0-9]`.

Обязательные поля:

| Поле | Значение |
|---|---|
| `type` | `"npc"` |
| `name` | русское имя |
| `folder` | `null` (Влад раскладывает сам) |
| `img` | `azlanti/portarits/{slug}.webp` (относительный путь, без https; можно `?{epoch_ms}` как кеш-бастер) |
| `prototypeToken.texture.src` | `tokenizer/npc-images/{slug}.token.webp` |
| `prototypeToken.ring.subject.texture` | тот же путь |
| `prototypeToken.disposition` | `-1` враг, `0` нейтрал, `1` союзник |
| `prototypeToken.actorLink` | `false` для рядовых, `true` для именных |
| `ownership.default` | `1` |
| `_stats` | `coreVersion`/`systemVersion` как выше, `exportSource.uuid = "Actor.{_id}"` |

**Токены Влад делает сам** через Tokenizer («использовать данные актёра») — путь в `texture.src` пишем заранее по slug, файла может ещё не быть, это нормально.

`system` (минимум): `attributes.hp/ac/speed`, `details.level.value`, `details.languages`, `abilities.*.mod`,
`perception.mod`, `saves.fortitude/reflex/will.value`, `skills.{skill}.base`, `traits.value` + `traits.size.value`.

`items` — массив. Типы: `melee` (Strike), `action` (способности/реакции), `spellcastingEntry` + `spell`,
`equipment`, `consumable`, `weapon`, `armor`, `lore`. У предметов из компендиума ставим
`_stats.compendiumSource = "Compendium.pf2e.<pack>.Item.<id>"` — тогда Babele подтягивает русский перевод.
Заклинания привязываются к энтри через `system.location.value = <_id спелл-энтри>` и список в `slots.slotN.prepared`.

**Канон сначала:** рядовым берём готовый стат-блок (Bestiary / GM Core / NPC Core / Absalom CoLO) и рескиним
именем + артом, как сделано с Каспаром. `npc-forge` — только если ничего не подошло.

## Сцена (без сетки и освещения)

Эталон: `fvtt-Scene-joren-komnatka-wQ6jOk5gtmaDwOyA.json`.
Шаблон-скелет: скрипт в scratchpad, см. ниже.

Имя файла: `fvtt-Scene-{slug}-{_id}.json`.

| Поле | Значение |
|---|---|
| `background.src` | `azlanti/Arts/{slug}.webp` |
| `width` / `height` | фактические размеры webp (у нас обычно `2528 × 1422`) |
| `thumb` | `worlds/kampejn-a/assets/scenes/{_id}-thumb.webp` |
| `grid.type` | `0` — **сетки нет** |
| `tokenVision` | `false` |
| `fog.exploration` | `false` |
| `environment.globalLight.enabled` | `false` |
| `environment.darknessLevel` | `0.0974` (как в эталоне) |
| `folder` | `v87QL00uIyey590F` (папка сцен кампании; старые PFS-сцены лежали в `3sNTz5tuifvLR312`) |
| `tokens`, `lights`, `walls`, `notes`, `sounds`, `regions`, `templates`, `tiles`, `drawings` | `[]` |
| `flags.pf2e-visioner.deletedEntryCache` / `partyTokenStateCache` | `{}` |

## Готовые скелеты

`scratchpad/foundry_templates/actor_npc_template.json` и `scene_template.json` —
плейсхолдеры `{{NAME}}`, `{{SLUG}}`, `{{ACTOR_ID}}`, `{{SCENE_ID}}`.
