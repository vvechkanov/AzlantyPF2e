// Опросник игроков Азланти — сентябрь 2026 (после С21).
// Вставить в script.google.com, запустить createSurvey. Ссылки — в журнале выполнения.
// Текст вопросов синхронизирован с Dev/Опросник_игроков_2026-09.md.

var PACE = ['Слишком медленно', 'Немного медленно', 'В самый раз', 'Немного быстро', 'Слишком быстро'];

function createSurvey() {
  var form = FormApp.create('Азланти: как вам игра?');
  form.setDescription(
    'Первая арка позади, вторая в самом разгаре — самое время свериться. ' +
    '5–10 минут. Честные ответы полезнее вежливых.'
  );
  form.setProgressBar(true);

  // --- Кампания в целом ---
  form.addSectionHeaderItem().setTitle('Кампания в целом');

  form.addTextItem().setTitle('Как тебя зовут?').setRequired(true);

  form.addScaleItem()
    .setTitle('Насколько тебе сейчас нравится кампания?')
    .setBounds(1, 10).setRequired(true);

  form.addScaleItem()
    .setTitle('Первая арка (Гринфорд, руины под деревней). Как она тебе в целом?')
    .setBounds(1, 10).setRequired(true);

  form.addScaleItem()
    .setTitle('Вторая арка (Абсалом) — как она тебе на данный момент?')
    .setBounds(1, 10).setRequired(true);

  // --- Темп и баланс ---
  form.addPageBreakItem().setTitle('Темп и баланс');

  form.addScaleItem()
    .setTitle('Насколько тебе понятно, что сейчас происходит и что партия может делать дальше?')
    .setBounds(1, 5).setLabels('совсем запутался', 'всё ясно')
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Темп сюжета (как быстро движется история)')
    .setChoiceValues(PACE).setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Темп внутри одной сессии (как быстро идут сцены за вечер)')
    .setChoiceValues(PACE).setRequired(true);

  form.addGridItem()
    .setTitle('Чего в игре хочется больше, а чего меньше?')
    .setRows([
      'Бои',
      'Разговоры с NPC',
      'Расследования и загадки',
      'Исследование новых мест',
      'Отыгрыш внутри партии',
      'Планирование и обсуждения'
    ])
    .setColumns(['Меньше', 'Так же', 'Больше'])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Сложность боёв')
    .setChoiceValues(['Слишком легко', 'Легковато', 'В самый раз', 'Тяжеловато', 'Слишком тяжело'])
    .setRequired(true);

  // --- Твой персонаж ---
  form.addPageBreakItem().setTitle('Твой персонаж');

  form.addScaleItem()
    .setTitle('Насколько тебе нравится, как развивается твой персонаж?')
    .setBounds(1, 5).setRequired(true);

  form.addScaleItem()
    .setTitle('Хватает ли твоему персонажу времени в кадре?')
    .setBounds(1, 5).setLabels('почти не играю', 'даже слишком много')
    .setRequired(true);

  // --- Что дальше ---
  form.addPageBreakItem().setTitle('Что дальше');

  form.addParagraphTextItem()
    .setTitle('Что обязательно продолжать — что тебе в игре нравится больше всего?')
    .setRequired(true);
  form.addParagraphTextItem().setTitle('Что стоит изменить или убрать?');
  form.addParagraphTextItem().setTitle('Чего в игре не хватает?');
  form.addParagraphTextItem().setTitle('Всё, что хочется сказать ГМу и не влезло выше.');

  Logger.log('Редактировать: ' + form.getEditUrl());
  Logger.log('Ссылка для игроков: ' + form.getPublishedUrl());
}
