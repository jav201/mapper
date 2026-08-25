# Prototipo: navegación, foco y carga en repo/mapas

**Pregunta:** ¿Cómo evitamos que el input secuestre las teclas globales, cómo mostramos progreso durante cargas lentas, y cómo presentamos la info de ramas con indicadores de estado más claros?

**Renders:** abrir `out/index.html` en el navegador.

**Variantes:**

- **A — formulario consciente del foco + barra de progreso + tabla**
  - El input existe en un panel centrado pero **no roba el foco** al entrar a la pantalla.
  - El usuario lo enfoca con `i`/`tab`; mientras no tiene foco, `j/k/q/1/2/3` funcionan globalmente.
  - Progreso como **etapas + barra horizontal** debajo de las tabs.
  - Tabla de ramas con columnas: rail, nombre, ahead, behind, CI, edad, estado resumido.

- **B — barra de comando deslizable + progreso inline + dashboard denso**
  - **No hay input visible por defecto**; se abre con `c` en la parte inferior estilo command palette.
  - Progreso inline junto al texto de estado (`cargando ramas ▰▰... 45% ◐ 3/6`).
  - Dashboard denso con mini timeline de ahead/behind por rama.

- **C — panel lateral con etapas + tabla agrupada**
  - Layout de dos paneles: a la izquierda input + etapas + barra; a la derecha tabla agrupada por tipo (releases, hotfixes, branches).
  - Útil si el repo crece y queremos organizar ramas por categoría.

**Fix técnico para el secuestro de teclas:**
Usar `Binding(..., priority=True)` en los bindings de pantalla para que `q`, `j`, `k`, `1/2/3` se evalúen antes de llegar al `Input`.

**Próximo paso:** elegir una variante (o mezcla) para integrar en `mapper/app.py` (`PlugRepoScreen` / `RepoScreen`).
