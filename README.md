# geodata_standartization
Стандартизация адресов без частого использования regex и с использованием генетического алгоритма (написан вручную, без библиотек), плюс оценка результата посредством дистанции Левеншетейна.<br />
Результат можно посмотреть в results.csv, третья колонка (result0). Имеются неточности там, где структура адреса сильно отличается или же есть ошибки в словах.<br />
Алгоритм сделал 10 итераций, но практически сразу попадает в локальный(?) минимум. Попытки изменить параметры наследования к успеху не привели.<br />
Финальный результат: ~.62 против образца ~.52 (пропорции к оригинальной выборке)<br />

