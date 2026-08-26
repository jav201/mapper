# mapper · variant A «taller» — resumen ejecutivo

**Batch `2026-08-25-ui-next-batch-01` · 2026-08-25**

---

## En una frase

El mapa dejó de ser un visor y pasó a ser un instrumento operable: la ficha de cada nodo ahora se
edita en el mismo lugar donde se navega, los adjuntos se abren desde ahí, y las acciones destructivas
piden confirmación.

## El problema

`mapper` se usa para *arqueología de sistemas legacy*: recorrer un mapa grande de un sistema heredado,
encontrar los nodos a los que les faltan datos obligatorios, y completarlos. Antes de este batch ese
recorrido se rompía en tres puntos:

1. **No se podía completar nada sin salir del mapa.** La ficha se mostraba —de hecho se dibujaba dos
   veces— pero no se editaba.
2. **La ayuda mentía.** De las 33 acciones que la paleta de comandos ofrecía, **ninguna se ejecutaba**.
   Y `ctrl+p` ni siquiera abría la paleta de mapper: abría la de la librería subyacente.
3. **`x` borraba un subárbol completo sin preguntar**, y el historial de deshacer se perdía al salir
   del mapa, así que lo borrado era irrecuperable.

## Lo que se entregó

| | |
|---|---|
| **Edición in-situ** | Panel derecho editable: título, estado, notas y cada campo del esquema. Los campos se etiquetan con su nombre real (`documento`), no con la letra interna (`D`). Los obligatorios vacíos se marcan. Todo se guarda en los archivos de texto, que siguen siendo la fuente de verdad. |
| **Adjuntos** | Agregar, abrir y quitar desde la ficha. Al abrir, el destino se valida antes de entregarlo al sistema operativo. |
| **Un solo teclado** | Un único archivo declara todas las teclas. La paleta, la ayuda (`?`) y la barra inferior leen esa misma declaración, así que **no pueden ofrecer una tecla que no funcione**. |
| **Lista de trabajo de cobertura** | Desde el reporte, `↵` salta al nodo **y deja el cursor en el primer campo que falta**. `n` avanza al siguiente hueco en todo el mapa. |
| **Seguridad** | Toda acción destructiva confirma primero, diciendo cuántos descendientes se llevará. El historial de deshacer vive a nivel de aplicación y sobrevive salir y volver a entrar. |

## Lo que se encontró por el camino

El valor de este batch no está solo en lo construido. **Se encontraron seis defectos que ya existían
y que las pruebas anteriores no podían ver**, porque viven en la distancia entre *"la acción se
ejecutó"* y *"la tecla que el operador presiona llega a la acción"* — más uno que este mismo batch
introdujo y que la revisión final detectó antes de integrar.

Tres merecen mención por su severidad:

- **Una ruta de adjunto podía abrir cualquier archivo del disco.** No se dedujo: se ejecutó. Se
  abrieron `calc.exe` y `powershell.exe` desde un mapa. Los mapas se comparten y se clonan, así que
  ese texto no es confiable. Ahora se rechaza todo lo que quede fuera del espacio de trabajo, **antes**
  de entregarlo al sistema.
- **`m cobertura` —la puerta de entrada al flujo principal— estaba cortada de la barra de teclas.**
  La barra se dibujaba a un ancho fijo y mostraba 9 de 17 atajos, sin decir que ocultaba algo.
- **Archivar la raíz vaciaba el mapa en disco.** Este defecto lo introdujo este batch, no lo heredó:
  la confirmación prometía *reemplazar* la raíz y en realidad borraba todo, dejando el archivo sin
  nodos. Lo encontró la revisión final; ahora esa acción se rechaza y hay una prueba que lo cubre.

## Sobre la calidad de la verificación

Las pruebas pasaron de **88 a 245**. Más relevante que el número: dos revisiones independientes
lograron **romper controles dejando la suite en verde** —cinco casos en total—, y en cada uno mis
propias pruebas de falsificación ya habían corrido y me habían convencido de lo contrario. La
revisión final encontró además un **defecto de pérdida de datos introducido por este mismo batch**:
archivar la raíz vaciaba el mapa en disco. Se corrigió y quedó cubierto por una prueba.

La lección quedó registrada y es la recomendación principal para el siguiente batch: **verificar un
control borrándolo no basta.** Borrarlo es la modificación más fácil de imaginar y la menos probable
en la práctica; lo que realmente ocurre es que alguien *reescribe la expresión* —una simplificación,
un refactor— y ahí es donde la suite dejaba pasar el error.

## Estado y siguiente paso

Listo para integrar. El siguiente batch es **variante B «atlas»**: navegación del lienzo a escala
—desplazamiento, plegado de ramas, minimapa— sobre el mismo esqueleto ya construido.

**Un punto de verificación que NO es una prueba automatizada.** El último salto —que el sistema
operativo efectivamente abra la aplicación asociada a un adjunto— no tiene forma honesta de
verificarse sin lanzar un programa real. Se verifica por **inspección** del código, no por prueba, y
así queda registrado (`MAN-01`). Las pruebas cubren toda la cadena hasta ese punto, pero no ese
salto: darlo por probado sería falso.

**Riesgos abiertos, declarados y no cerrados en silencio:** un archivo lateral mal formado todavía
puede impedir cargar un mapa completo; cuatro pantallas modales aún no leen la declaración única de
teclas; y quedan detalles de seguridad menores registrados como pendientes explícitos.
