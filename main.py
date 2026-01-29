

from nicegui import ui,app
from database import Database
from models import Vino, Nota,FiltrosVino
import time
from auth import AuthDatabase
import os


db = Database()
auth_db = AuthDatabase()

SESSION_TIMEOUT = 30 * 60 # 30 minutos

# def sesion_valida(user: dict) -> bool:
#     return (
#         'user' in user and
#         'login_time' in user and
#         (time.time() - user['login_time']) < SESSION_TIMEOUT
#     )


# def login(username, password):
#     user_id = auth_db.verificar_usuario(username, password)

#     if not user_id:
#         ui.notify('Usuario o contraseña incorrectos', type='negative')
#         return

#     user = app.storage.user
#     user['user'] = user_id
#     user['login_time'] = time.time()
#     ui.navigate.to('/')

# def logout():
#     app.storage.user.clear()
#     ui.navigate.to('/login')

# @ui.page('/login')
# def login_page():
#     with ui.card().classes('w-96 mx-auto mt-40'):
#         ui.label('🍷 Vinoteca').classes('text-xl font-bold text-center')
#         usuario = ui.input('Usuario')
#         password = ui.input('Contraseña', password=True)

#         ui.button(
#             'Entrar',
#             on_click=lambda: login(usuario.value, password.value)
#         ).classes('w-full bg-blue')

@ui.page('/login')
def login_page():
    with ui.card().classes('w-96 mx-auto mt-40'):
        ui.label('🍷 Vinoteca').classes('text-xl font-bold text-center')
        usuario = ui.input('Usuario')
        password = ui.input('Contraseña', password=True)

        def do_login():
            user_id = auth_db.verificar_usuario(usuario.value, password.value)
            if not user_id:
                ui.notify('Usuario o contraseña incorrectos', type='negative')
                return

            app.storage.user['user'] = user_id
            app.storage.user['login_time'] = time.time()
            ui.navigate.to('/')

        ui.button('Entrar', on_click=do_login).classes('w-full bg-blue')


@ui.page('/')
def vinoteca():
    user = app.storage.user

    if (
        'user' not in user or
        'login_time' not in user or
        time.time() - user['login_time'] > SESSION_TIMEOUT
    ):
        user.clear()
        ui.navigate.to('/login')
        return

    # sliding expiration
    user['login_time'] = time.time()

    def logout():
        user.clear()
        ui.navigate.to('/login')

    ui.button('Salir', icon='logout', on_click=logout)

    # ⬇⬇⬇ AQUÍ VA TODO TU CÓDIGO DE VINOTECA ⬇⬇⬇

        # ⬇⬇⬇ AQUÍ VA TODO TU CÓDIGO DE VINOTECA ⬇⬇⬇
        # (exactamente el que ya tenías)
    # nuevo_vino = Vino()
    filtros = FiltrosVino()

    # --- DISEÑO DE LA PÁGINA ---
    with ui.column().classes('w-full'):
        ui.label('Mi vinoteca').classes('text-center text-6xl w-full')
        ui.separator().classes('bg-black')


    lista_vinos = ui.column().classes('w-full') # Contenedor para los vinos de la vinoteca

    # Actualizamos el contenido de la vinoteca y lo presentamos.
    def refrescar_contenido() -> None:
        '''
        Función para refrescar el contenido de la página y que muestra todos los vinos que hay en la bodega
        '''
        lista_vinos.clear() # Contenedor para almacenar los vinos de la bodega
        vinos = db.obtener_vinos(filtros)

        with lista_vinos: # Columna layout
            if not vinos:
                ui.label('La bodega está vacía').classes('text-gray italic')
            # Creamos un contenedor grid que define 4 columnas en pantallas medianas/grandes
            # 'grid-cols-1' para móviles y 'md:grid-cols-4' para escritorio
            with ui.element('div').classes('grid grid-cols-1 md:grid-cols-4 gap-4 w-full'):
                for v in vinos:
                    # Definimos los colores
                    colores = {
                        'Tinto': ('fuchsia-600','white'),
                        'Blanco': ('lime-300','black'),
                        'Rosado': ('pink', 'white'),
                        'Espumoso rosado': ('rose-400', 'black'),
                        'Espumoso': ('amber-300', 'black')
                    }
                    color_bg, color_txt = colores.get(v.tipo)

                    # Creamos una card para cada vino
                    with ui.card().classes('w-full shadow-md border-l-4 '):
                        # CABECERA DE LA CARD
                        with ui.row().classes('w-full justify-between items-start no-wrap'):
                            with ui.column().classes('gap-0'):
                                ui.label(v.nombre).classes('text-xl font-bold leading-tight').style("text_color: {color_bg}")                            
                                ui.label(v.bodega).classes('text-sm text-gray-500')
                                ui.badge(v.tipo, color=color_bg, text_color=color_txt).classes('text-xs font-mono')
                            # Botones para edición/eliminación de cada vino
                            with ui.column().classes('gap-1 items-left'):                            
                                ui.button(icon='edit_document',color='green',on_click=lambda v=v: actualizar_vino(v)).props('size=10px')
                                ui.button(icon='o_delete',color='red',on_click=lambda v=v: confirmar_eliminacion_vino(v)).props('size=10px')                       

                        ui.separator()
                        # CUERPO ALINEADO (Usando el método de etiquetas alineadas)
                        with ui.grid(columns='100px auto').classes('w-full text-sm gap-y-1'):
                            ui.label('Cosecha:').classes('font-semibold text-gray-500')
                            ui.label(str(v.cosecha))                        
                            ui.label('País:').classes('font-semibold text-gray-500')
                            ui.label(f"{v.pais}")
                            ui.label("D.O:").classes('font-semibold text-gray-500')
                            ui.label(f"{v.denominacion}").classes('font-mono font-semibold')
                            #with ui.row().classes('w-full items-stretch'):
                            ui.label('Stock:').classes('font-semibold text-gray-500')
                            if v.disponible():
                                ui.label(f"{v.cantidad} unidades").classes('font-bold text-blue-600')
                            else:
                                ui.label(f"{v.cantidad} unidades").classes('font-bold text-red-600')
                            with ui.row():
                                ui.button(icon='add',color='white',on_click=lambda v_id=v.id, stock=v.cantidad: variar_stock(v_id,stock + 1)).classes('w-1')
                                ui.button(icon='remove',color='white',on_click=lambda v_id=v.id, stock=v.cantidad: variar_stock(v_id,stock - 1)).classes('w-1')
                            with ui.row():
                                if v.guarda:
                                    ui.label(f"Vino de guarda").classes('font-semibold text-red-400')
                                    ui.label(f"Consumir hasta {v.fechaConsumo}").classes('font-semibold text-red-400')
                        # FICHA TÉCNICA (Desplegable compacto)
                        with ui.expansion('Ficha Técnica', icon='description',value=False).classes('w-full bg-gray-200 mt-2'):
                            ui.markdown(f"**Uvas:** {v.variedad1} {v.porcentajeVariedad1}%")
                            if v.variedad2:
                                ui.label(f"{v.variedad2} {v.porcentajeVariedad2}%").classes('text-xs')
                            if v.variedad3:
                                ui.label(f"{v.variedad3} {v.porcentajeVariedad3}%").classes('text-xs')
                            if v.variedad4:
                                ui.label(f"{v.variedad4} {v.porcentajeVariedad4}%").classes('text-xs')
                            ui.separator().classes('my-2')
                            ui.label(v.fichaTecnica).classes('text-xs italic')
                        nueva_nota = Nota()
                        with ui.grid(columns=3).classes('w-full gap-4 items-stretch'):
                            # Añadir una nueva nota de cata
                            with ui.expansion('Añadir nota de cata', icon='edit_note').classes('col-span-3 flex flex-col bg-blue-100 mt-2'):
                                ui.date_input("Fecha").bind_value(nueva_nota,'fechaCata')
                                ui.textarea('Notas:').classes('w-full text-gray-200 text-xs italic').props('autogrow').bind_value(nueva_nota,'notaCata')
                                ui.label("Valoración:").classes('text-sm italic')
                                ui.rating(value=0,max=10,icon='star').bind_value(nueva_nota,'valoracion')
                                ui.button("GUARDAR NOTA DE CATA", on_click=lambda v_id=v.id, n=nueva_nota: guardar_cata(v_id,n)).classes('w-full bg-blue')
                            # Mostrar todas las notas de cata asociadas a un vino
                            catas = leer_catas(v.id)
                            if catas:
                                with ui.expansion('Notas de cata', icon='wine_bar').classes('col-span-3 bg-green-100'):
                                    for c in catas:
                                        ui.label(f"{c.fechaCata}:").classes('font-bold text-sm')
                                        ui.label(f"{c.notaCata}")
                                        ui.separator()                                    
                                        ui.label("Valoración:").classes('text-bold italic')
                                        ui.rating(value=c.valoracion,max=10,color='black')
                                        ui.separator()

    def guardar_vino() -> None:
        '''
        Función para guardar un nuevo vino en la base de datos.
        '''

        if not nuevo_vino.nombre:
            ui.notify('El nombre del vino es obligatorio',type='negative')
            return
        if nuevo_vino.cantidad < 0:
            ui.notify("Cantidad inválida",type='negative')
            return

        db.insertar_nuevo_vino(nuevo_vino)
        ui.notify(f'Vino {nuevo_vino.nombre} añadido a la colección',type='positive') 
        dialogo_añadir_vino.close()   
        refrescar_contenido()

    def guardar_cata(vino_id: int,nota: Nota) -> None:
        '''
        Función para añadir una nueva nota de cata a un vino

        :param vino_id: id del vino al que se va a asociar la nueva nota de cata
        :type vino_id: int
        :param nota: nota de cata
        :type nota: Nota
        '''
        if not nota.fechaCata or not nota.notaCata:
            ui.notify('Completa la fecha y la nota', type='negative')
            return

        db.agregar_cata(vino_id,nota.notaCata,nota.fechaCata,nota.valoracion)
        ui.notify('Nota de cata guardada', type='positive')
        refrescar_contenido()

    def leer_catas(vino_id: int) -> list:
        '''
        Función para recuperar y leer las catas asociadas a un vino

        :param vino_id: la id del vino al que se va a añadir la cata
        :type vino_id: int
        :return: Retorna las catas asociadas al vino con id vino_id
        :rtype: list
        '''
        catas = db.obtener_catas(vino_id)
        return catas

    def confirmar_eliminacion_vino(vino: Vino) -> None:
        '''
        Función para confirmar el borrado del vino y evitar borrados accidentales. Función de seguridad.

        :param vino: Instancia de un vino
        :type vino: Vino
        '''
        with ui.dialog() as dialogo:
            with ui.card().classes():
                ui.label("Esto eliminará el vino y todas las catas asociadas.").classes('font-bold text-red-500')
                ui.label(f"¿Realmente quieres eliminar el vino {vino.nombre}?").classes('font-bold text-red-500')

                with ui.row().classes('w-full items-stretch'):
                    ui.button("Eliminar",icon="o_delete",color='white',on_click=lambda vino_id=vino.id,nombre=vino.nombre:eliminar_vino(vino_id,nombre))
                    ui.button("Cancelar",icon='o_cancel',color='red',on_click=dialogo.close)

        dialogo.open()

    def eliminar_vino(vino_id: int, nombre: str) -> None:
        '''
        Función para eliminar un vino de la base de datos

        :param vino_id: La id del vino que se va a eliminar
        :type vino_id: int
        :param nombre: Nombre del vino que se va a eliminar
        :type nombre: str
        '''
        if db.borrar_vino(vino_id):
            ui.notify(f"{nombre} eliminado correctamente",type='positive')
            dialogo_añadir_vino.close()
            refrescar_contenido()
        else:
            ui.notify("No se pudo eliminar el vino",type='negative')

    def variar_stock(vino_id:int,stock:int) -> None:

        if stock < 0:
            ui.notify("Stock cero",type='negative')
            return
        else:
            db.actualizar_stock(vino_id,stock)
            ui.notify("Stock actualizado",type='positive')
            refrescar_contenido()

    def actualizar_vino(vino: Vino) -> None:
        '''
        Función para actualizar los valores de un vino

        :param vino: El objeto Vino que vamos a modificar
        :type vino: Vino
        '''
        dialogo_actualizar_vino = ui.dialog()
        dialogo_actualizar_vino.open()

        with dialogo_actualizar_vino:
            with ui.card().classes('w-full'):
                ui.label("Editar vino").classes('text-lg font-bold')
                with ui.element('div').classes('grid grid-cols-2 gap-4 w-full'):                
                    ui.input('Nombre',value=vino.nombre).bind_value(vino,'nombre')
                    ui.number('Cosecha',value=vino.cosecha).bind_value(vino,'cosecha')
                    ui.select(['Tinto','Blanco','Rosado','Espumoso','Espumoso rosado'],label='Tipo',with_input=True,value=vino.tipo)
                    ui.input('Bodega',value=vino.bodega)
                    ui.input('Pais',value=vino.pais)
                    ui.input('Denominación',value=vino.denominacion)
                    ui.switch('Vino de guarda',value=vino.guarda)
                    ui.number('Fecha de consumo',value=vino.fechaConsumo,min=2000)
                    ui.number('Cantidad',value=vino.cantidad,min=1)

                with ui.expansion('FICHA TÉCNICA',icon='description').classes('w-full bg-gray-200 border'):
                    with ui.element('div').classes('grid grid-cols-2 gap-4 w-full'):
                        ui.input("Variedad principal",value=vino.variedad1)
                        ui.number('Porcentaje variedad principal',value=vino.porcentajeVariedad1,format='%d',max=100,min=0)
                        ui.input("Variedad 2",value=vino.variedad2)
                        ui.number('Porcentaje variedad 2',value=vino.porcentajeVariedad2,format='%d',max=100,min=0)
                        ui.input("Variedad 3",value=vino.variedad3)
                        ui.number('Porcentaje variedad 3',value=vino.porcentajeVariedad3,format='%d',max=100,min=0)
                        ui.input("Variedad 4",value=vino.variedad4)
                        ui.number('Porcentaje variedad 4',value=vino.porcentajeVariedad4,format='%d',max=100,min=0)
                    ui.textarea('Elaboración',value=vino.fichaTecnica).classes('w-full')
                ui.button("GUARDAR",on_click=lambda: (guardar_vino_actualizado(vino),dialogo_actualizar_vino.close()))
                # ui.button("CERRAR",on_click=dialogo_actualizar_vino.close)

    def guardar_vino_actualizado(vino: Vino) -> None:
        db.actualizar_vino(vino)
        refrescar_contenido()
        ui.notify("Vino actualizado",type='positive')
        return

    dialogo_añadir_vino = ui.dialog()
    # --- Sección para añadir un nuevo vino a la base de datos ---
    with dialogo_añadir_vino:
        nuevo_vino = Vino()

        with ui.card().classes('w-[1200px] overflow-y-auto'):
            ui.label('Añadir nuevo vino').classes('text-xl font-bold')
            nombre = ui.input('Nombre').bind_value(nuevo_vino,'nombre')
            cosecha = ui.number('Cosecha',value=2024,format='%d').bind_value(nuevo_vino,'cosecha')
            tipo = ui.select(['Tinto','Blanco','Rosado','Espumoso','Espumoso rosado'],label='Tipo',with_input=True).bind_value(nuevo_vino,'tipo')
            bodega = ui.input('Bodega').bind_value(nuevo_vino,'bodega')
            pais = ui.input('Pais').bind_value(nuevo_vino,'pais')
            denominacion = ui.input('Denominación').bind_value(nuevo_vino,'denominacion')
            guarda = ui.switch('Vino de guarda').bind_value(nuevo_vino,'guarda')
            fechaConsumo = ui.number('Fecha de consumo',value=2024,min=2000).bind_visibility_from(guarda,'value').bind_value(nuevo_vino,'fechaConsumo')
            stock = ui.number('Cantidad',min=1).bind_value(nuevo_vino,'cantidad')

            with ui.expansion('FICHA TÉCNICA',icon='description').classes('w-full bg-gray-200 border'):
                with ui.element('div').classes('grid grid-cols-2 gap-4 w-full'):
                    uva1 = ui.input("Variedad principal").bind_value(nuevo_vino,'variedad1')
                    porcentajeUva1 = ui.number('Porcentaje variedad principal',value=0,format='%d',max=100,min=0).bind_value(nuevo_vino,'porcentajeVariedad1')
                    uva2 = ui.input('Variedad 2').bind_value(nuevo_vino,'variedad2')
                    porcentajeUva2 = ui.number('Porcentaje variedad 2',value=0,format='%d').bind_value(nuevo_vino,'porcentajeVariedad2')
                    uva3 = ui.input("Variedad 3").bind_value(nuevo_vino,'variedad3')
                    porcentajeUva3 = ui.number('Porcentaje variedad 3',value=0,format='%d').bind_value(nuevo_vino,'porcentajeVariedad3')
                    uva4 = ui.input('Variedad 4').bind_value(nuevo_vino,'variedad4')
                    porcentajeUva4 = ui.number('Porcentaje uva 4',value=0,format='%d').bind_value(nuevo_vino,'porcentajeVariedad4')
                notaElaboracion = ui.textarea('Elaboración').classes('w-full').bind_value(nuevo_vino,'fichaTecnica')
            ui.button('GUARDAR VINO',on_click=lambda: (guardar_vino(),dialogo_añadir_vino.close()))
            ui.button('CERRAR', on_click=dialogo_añadir_vino.close)              

    ui.button('AÑADIR NUEVO VINO',on_click=dialogo_añadir_vino.open).classes('w-full bg-blue')

    # Panel de filtros
    with ui.card().classes('w-full mb-4'):
        ui.label("Filtros").classes('font-bold text-lg')

        with ui.row().classes('w-full items-end gap-4'):
            ui.number("Cosecha",min=2000).classes('text-gray').bind_value(filtros,'cosecha')
            ui.input("Denominacion").classes('text-gray').bind_value(filtros,'denominacion')
            ui.select(['Tinto','Blanco','Rosado','Espumoso rosado','Espumoso'],label='Tipo',with_input=True).bind_value(filtros,'tipo')
            ui.input("Pais").classes('text-black').bind_value(filtros,'pais')
            ui.number("Cantidad").classes('text-black').bind_value(filtros,'cantidad')
            ui.checkbox("Sin stock").bind_value(filtros,'sinStock')
            ui.button(
                text='Aplicar',
                icon='o_filter_alt',
                on_click=refrescar_contenido
            )
            ui.button(
                text="Limpiar",
                icon='clear',
                on_click=lambda: (
                    setattr(filtros,'cosecha',None),
                    setattr(filtros,'denominacion',None),
                    setattr(filtros,'tipo',None),
                    setattr(filtros,'pais',None),
                    setattr(filtros,'cantidad',None),
                    setattr(filtros,'sinStock',False),
                    refrescar_contenido()),

            )
    refrescar_contenido()       

ui.run(
    title='Vinoteca',
    storage_secret='9562lsir$6&/((kagj#5634234fgasgsñfgañ.qw-',
    )

