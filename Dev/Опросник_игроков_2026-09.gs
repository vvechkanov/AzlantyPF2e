// Опросник игроков Азланти — сентябрь 2026 (после С21).
// Вставить в script.google.com, запустить createSurvey. Ссылки — в журнале выполнения.
// Текст вопросов синхронизирован с Dev/Опросник_игроков_2026-09.md.

function createSurvey() {
  var form = FormApp.create('Азланти: куда двигаемся дальше');
  form.setDescription(
    'Опрос после 21-й сессии. 7–10 минут. Честные ответы полезнее вежливых — ' +
    'от них зависит, как пройдут следующие 3–5 сессий арки.'
  );
  form.setProgressBar(true);

  // --- Блок 1. Общее ---
  form.addSectionHeaderItem().setTitle('Общее');

  form.addTextItem().setTitle('Как тебя зовут?').setRequired(true);

  form.addScaleItem()
    .setTitle('Насколько тебе сейчас нравится кампания?')
    .setBounds(1, 5).setLabels('мучаюсь', 'жду каждую сессию')
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('За 21 сессию в игре прошло около 11 дней. Как тебе такой темп?')
    .setChoiceValues(['Слишком медленно', 'Немного медленно', 'В самый раз', 'Немного быстро', 'Слишком быстро'])
    .setRequired(true);

  form.addGridItem()
    .setTitle('Чего тебе хочется больше, а чего меньше?')
    .setRows([
      'Бои',
      'Разговоры с NPC',
      'Расследования и загадки',
      'Исследование новых мест',
      'Разговоры внутри партии',
      'Планирование и логистика («кто куда идёт завтра»)'
    ])
    .setColumns(['Меньше', 'Так же', 'Больше'])
    .setRequired(true);

  var scenes = form.addCheckboxItem()
    .setTitle('Какие сцены последних сессий понравились больше всего? (до трёх)')
    .setChoiceValues([
      'Спор с Дэленом в лесу',
      'Исповедь Бель у Эниса',
      'Лисенг в библиотеке',
      'Разговор с Хоуп о переезде приюта',
      'Отправка Сески на задание',
      'Арена: львицы против хобгоблинов',
      'Баня «Первоцвет» целиком',
      'Подбор ароматов у Ильсабет',
      'Вечер в приюте: ветка и Гранд-Холт'
    ])
    .showOtherOption(true);
  scenes.setValidation(FormApp.createCheckboxValidation().requireSelectAtMost(3).build());

  form.addParagraphTextItem().setTitle('Было ли что-то скучным или затянутым?');

  // --- Блок 2. Сюжет ---
  form.addPageBreakItem().setTitle('Сюжет');

  form.addGridItem()
    .setTitle('Что делать с каждой ниткой?')
    .setRows([
      'Свора Дэлена и тюрьма Луж',
      'Грайма у гоблинов и спектакль Зусгута',
      'Встреча с Валастиром',
      'Музей Блакросов и молот',
      'Сын Гельдалы и посольство эльфов',
      'Статуэтка Киран и Холомог',
      'Безопасность приюта Хоуп',
      'Клык Кула и Джерикелла',
      'Гринфорд и обещание вернуться',
      'Черенок Гранд-Холта и Круг Камней'
    ])
    .setColumns(['Играть сейчас', 'Можно позже', 'Закрыть за кадром, без меня', 'Не помню, что это'])
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle('Представь, что следующие 3–5 сессий — финал арки в Абсаломе. Чем бы тебе хотелось, чтобы она закончилась?')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Чего твой персонаж хочет прямо сейчас больше всего?')
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Партия не успела что-то сделать к сроку. Как должен реагировать мир?')
    .setChoiceValues([
      'Мир ждёт нас: пока не пришли, ничего не происходит',
      'Что-то решается без нас, но мягко',
      'Не успели — значит, упустили. Это честно'
    ])
    .setRequired(true);

  // --- Блок 3. За столом ---
  form.addPageBreakItem().setTitle('За столом');

  form.addScaleItem()
    .setTitle('Хватает ли твоему персонажу времени в кадре?')
    .setBounds(1, 5).setLabels('почти не играю', 'даже слишком много')
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Иногда важное решение принимает часть группы (например, когда кто-то уже ушёл). Как лучше?')
    .setChoiceValues([
      'Нормально, так бывает',
      'Лучше откладывать до общего сбора',
      'Можно принимать, но коротко сообщать остальным в чате'
    ])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Насколько подробно вести деньги и покупки?')
    .setChoiceValues([
      'Подробно: каждая монета и цена',
      'Кратко: крупные траты считаем, мелочь нет',
      'Абстрактно: «можете себе позволить / не можете»'
    ])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Интересен ли тебе отдельный длинный ваншот на ~5 сессий (пятница/суббота)?')
    .setChoiceValues(['Да', 'Может быть', 'Нет'])
    .setRequired(true);

  form.addParagraphTextItem().setTitle('Одна вещь, которую ГМу стоит изменить.');
  form.addParagraphTextItem().setTitle('Одна вещь, которую обязательно надо оставить как есть.');

  Logger.log('Редактировать: ' + form.getEditUrl());
  Logger.log('Ссылка для игроков: ' + form.getPublishedUrl());
}
