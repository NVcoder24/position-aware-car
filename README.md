# position-aware-car
Машинка, которая знает о своём положении в пространстве по меткам ARUCO

Метки с id 1-4 нужны бля калибровки пространства

Метка с id 5 находится на машинке

Софт фиксит перспективу по 4 точкам (метки id 1-4) и переносит точки краёв меток в новую систему координат.
из этого можно подсчитать положение машинки в новой системе координат, а так же вектор
её направления.

Из этого можно строить маршруты перемещения и выполнять разные задачи.

В пример приведено поддержание направления машинки на PID регуляторе.

# Материалы
![alt text](https://github.com/NVcoder24/position-aware-car/blob/main/stuff/scheme1.png)
![alt text](https://github.com/NVcoder24/position-aware-car/blob/main/stuff/photo1.jpg)
![alt text](https://github.com/NVcoder24/position-aware-car/blob/main/stuff/photo2.jpg)
