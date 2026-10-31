import flet as ft
import sys
import json
import os
import shutil
from fractions import Fraction
import asyncio

AXIS_CENTER = ft.MainAxisAlignment.CENTER
CROSS_AXIS_CENTER = ft.CrossAxisAlignment.CENTER
CENTER = ft.Alignment.CENTER
BOTTOM_LEFT = ft.Alignment.BOTTOM_LEFT
BOTTOM_RIGHT = ft.Alignment.BOTTOM_RIGHT
SRCOUNT = 0
SRTIME = 1

DUPLICATE_SPRITE_DIC = {
    f"Zygarde 10% Forme Aura Break": "zygarde 10",
    f"Zygarde 10% Forme Power Construct": "zygarde 10",
    f"Zygarde 50% Forme Aura Break": "zygarde 50",
    f"Zygarde 50% Forme Power Construct": "zygarde 50",
    "Rockruff Own Tempo": "rockruff",
    "Sinistea Phony Form": "sinistea",
    "Sinistea Antique Form": "sinistea",
    "Polteageist Phony Form": "polteageist",
    "Polteageist Antique Form": "polteageist",
    "Poltchageist Counterfeit Form": "poltchageist",
    "Poltchageist Artisan Form": "poltchageist",
    "Sinistcha Counterfeit Form": "sinistcha",
    "Sinistcha Artisan Form": "sinistcha",
    "Minior Red Core": "minior",
    "Minior Orange Core": "minior",
    "Minior Yellow Core": "minior",
    "Minior Green Core": "minior",
    "Minior Blue Core": "minior",
    "Minior Indigo Core": "minior",
    "Minior Violet Core": "minior",
    "Torchic Male": "torchic",
    "Torchic Female": "torchic",
    "Quagsire Male": "quagsire",
    "Quagsire Female": "quagsire",
    "Bidoof Male": "bidoof",
    "Bidoof Female": "bidoof",
    "Buizel Male": "buizel",
    "Buizel Female": "buizel",
    "Floatzel Male": "floatzel",
    "Floatzel Female": "floatzel"
}

compiledPath = os.getenv("FLET_APP_STORAGE_DATA")

if compiledPath:
    savePath = os.path.join(compiledPath, 'CountSave.json')

    if not os.path.exists(savePath):
        if getattr(sys, 'frozen', False):
            basePath = sys._MEIPASS
        else:
            basePath = os.path.dirname(__file__)

        try:
            assetsSavePath = os.path.join(
                basePath, 'assets', 'CountSave.json')
            shutil.copy(assetsSavePath, savePath)
        except Exception:
            raise Exception(
                "CountSave.json is missing or could not be copied from assets.")

else:
    baseDir = os.path.dirname(__file__)
    savePath = os.path.join(baseDir, 'CountSave.json')

    if not os.path.exists(savePath):
        try:
            assetsSavePath = os.path.join(baseDir, 'assets', 'CountSave.json')
            shutil.copy(assetsSavePath, savePath)
        except Exception:
            raise Exception(
                "CountSave.json is missing or could not be copied from assets.")

pokemonDictionary = {}

if os.path.exists(savePath):
    try:
        with open(savePath, 'r', encoding="utf-8") as getSave:
            pokemonDictionary = json.loads(getSave.read())
    except (json.JSONDecodeError, IOError):
        raise Exception("CountSave.json is corrupt.")

else:
    raise Exception("CountSave.json is missing.")

def main(page: ft.Page):
    page.title = "Pokémon Shiny Tracker"
    activeHunt = "Bulbasaur"
    activeTile = None
    softResetKey = " "
    probabilityFloat = 1/4096
    probabilityString = "1/4096"
    count = 0
    binomial = "0%"
    totalTime = 0
    play = False
    timerTask = None

    activeHuntText = ft.Text(activeHunt, size=24)
    countText = ft.Text(str(count), size=150)
    binomialText = ft.Text(binomial, size=24)
    probabilityText = ft.Text(probabilityString, size=24)
    spriteContent = ft.Image(src="sprites/bulbasaur.webp", scale=1.2)

    def update():
        nonlocal count, totalTime
        global DUPLICATE_SPRITE_DIC

        try:
            count = pokemonDictionary[activeHunt][SRCOUNT]
            totalTime = pokemonDictionary[activeHunt][SRTIME]
        except KeyError:
            raise Exception(f"Couldn't find Pokémon named {activeHunt}.")

        countText.value = str(count)
        updateBinomial()

        minutes, seconds = divmod(totalTime, 60)
        hours, minutes = divmod(minutes, 60)
        playButton.content.value = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        playButton.update()

        # Flet takes up so much space so instead of a file per Pokemon,
        # these handle image overlaps
        def handleSpritePath(fileName):
            nonlocal spriteSubPath

            spriteSubPath = f"sprites/{fileName}.webp"

        if activeHunt in DUPLICATE_SPRITE_DIC:
            handleSpritePath(DUPLICATE_SPRITE_DIC[activeHunt])

        elif 'Alcremie' in activeHunt:
            alcremieType = activeHunt.split()[1]
            handleSpritePath("alcremie " + alcremieType.lower())

        else:
            spriteSubPath = f"sprites/{activeHunt.lower()}.webp"

        currentAssetsPath = os.getenv(
            "FLET_ASSETS_DIR", 
            os.path.join(os.path.dirname(__file__), "assets")
        )

        fullSpritePath = os.path.join(currentAssetsPath, spriteSubPath)

        if os.path.isfile(fullSpritePath):
            spriteContent.src = spriteSubPath
        else:
            spriteContent.src = "sprites/error.webp"

        activeHuntText.value = activeHunt
        page.update()

    def updateBinomial():
        nonlocal count, binomial

        if count == 0:
            binomial = "0%"
        else:
            binomial = str(
                round((1-(1-probabilityFloat)**count)*100, 2)) + "%"

        binomialText.value = binomial
        binomialText.update()

    def save():
        nonlocal count, activeHunt

        pokemonDictionary[activeHunt] = [count, totalTime]
        with open(savePath, 'w', encoding='utf-8') as saveFile:
            saveFile.write(
                json.dumps(
                    pokemonDictionary, indent=4, ensure_ascii=False))

    def closeWindow(e: ft.WindowEventType):
        save()
        page.window.destroy()

    page.window.on_event = closeWindow

    def closeApp(e: ft.AppLifecycleStateChangeEvent):
        if e.state in [
            ft.AppLifecycleState.PAUSE,
            ft.AppLifecycleState.HIDE,
            ft.AppLifecycleState.DETACH
            ]:

            save()

    page.on_app_lifecycle_state_change = closeApp

    def add(e):
        nonlocal count, binomial

        count += 1
        pokemonDictionary[activeHunt][SRCOUNT] = count
        countText.value = str(count)
        countText.update()

        updateBinomial()

    def subtract(e):
        nonlocal count, binomial
        
        if count > 0:
            count -= 1
            pokemonDictionary[activeHunt][SRCOUNT] = count
            countText.value = str(count)
            countText.update()

        updateBinomial()

    def updateTime():
        nonlocal totalTime

        minutes, seconds = divmod(totalTime, 60)
        hours, minutes = divmod(minutes, 60)
        timeString = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        playButton.content.value = timeString
        playButton.update()

    async def stopWatch():
        nonlocal totalTime, play

        while play:
            await asyncio.sleep(1)
            if not play:
                break
            totalTime += 1
            updateTime()

    def playPause(e):
        nonlocal play, timerTask

        play = not play
        if play:
            timerTask = page.run_task(stopWatch)
        else:
            pass

    def keyAdd(e: ft.KeyboardEvent):
        if e.key == softResetKey:
            add(e)

    def itemClick(e):
        nonlocal activeHunt, activeTile

        save()
        oldPokemon = activeHunt
        activeHunt = e.control.data

        if activeTile:
            activeTile.selected = False
        
        e.control.selected = True
        activeTile = e.control
        update()

    page.on_keyboard_event = keyAdd

    def edit(e):
        countInput.value = str(count)
        numberContainer.content = countInput
        numberContainer.update()
        countInput.focus()

    def submit(e):
        nonlocal count
        
        try:
            new_count = int(countInput.value)
            if new_count >= 0:
                count = new_count
                pokemonDictionary[activeHunt][SRCOUNT] = count
                countText.value = str(count)
                updateBinomial()
                save()
        except ValueError:
            pass
        
        numberContainer.content = countTextWrapper
        numberContainer.update()

    def filterPokemon(e=None):
        nonlocal activeTile

        query = (searchInput.value or '').lower()
        pokemonList.controls.clear()
        activeTile = None
        for key in pokemonDictionary.keys():
            if query in key.lower():
                isActive = (key == activeHunt)

                tile = ft.ListTile(
                    title=ft.Text(
                        f"{key} - {
                            pokemonDictionary[activeHunt][SRCOUNT]}",
                        size=20),
                    data=key,
                    selected=isActive,
                    on_click=itemClick,
                )

                pokemonList.controls.append(tile)

                if isActive:
                    activeTile = tile

        pokemonList.update()

    searchInput = ft.TextField(
        hint_text="Search Pokémon...",
        expand=True,
        on_change=filterPokemon
    )

    searchButton = ft.IconButton(
        icon=ft.Icons.SEARCH,
        on_click=filterPokemon,
    )

    countInput = ft.TextField(
        value=str(count),
        text_size=60,
        text_align=ft.TextAlign.CENTER,
        on_submit=submit,
        on_blur=submit,
    )

    countTextWrapper = ft.GestureDetector(
        content=countText,
        on_double_tap=edit
    )

    numberContainer = ft.Container(
        content=countTextWrapper,
        alignment=ft.Alignment.CENTER,
        expand=1
    )

    def editProbability(e):
        probabilityInput.value = probabilityString
        probabilityContainer.content = probabilityInput
        probabilityContainer.update()
        probabilityInput.focus()

    def submitProbability(e):
        nonlocal probabilityFloat, probabilityString

        try:
            val = probabilityInput.value.strip()
            if "/" in val:
                frac = Fraction(val)
            else:
                f_val = float(val)
                if f_val > 1:
                    frac = Fraction(1, int(f_val))
                else:
                    frac = Fraction(val)
            
            probabilityFloat = float(frac)
            probabilityString = str(frac)
            probabilityText.value = probabilityString
            updateBinomial()
        except Exception:
            pass
        
        probabilityContainer.content = probabilityTextWrapper
        page.update()

    probabilityInput = ft.TextField(
        value=probabilityString,
        text_size=20,
        text_align=ft.TextAlign.CENTER,
        on_submit=submitProbability,
        on_blur=submitProbability,
    )

    probabilityTextWrapper = ft.GestureDetector(
        content=probabilityText,
        on_double_tap=editProbability
    )

    probabilityContainer = ft.Container(
        content=probabilityTextWrapper,
        alignment=ft.Alignment.CENTER_RIGHT,
        expand=1
    )

    addButton = ft.IconButton(
        icon=ft.Icons.ADD,
        bgcolor=ft.Colors.GREEN,
        on_click=add,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=0)),
        expand=True,
        height=60
    )

    subtractButton = ft.IconButton(
        icon=ft.Icons.REMOVE,
        bgcolor=ft.Colors.RED,
        on_click=subtract,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=0)),
        expand=True,
        height=60
    )

    playButton = ft.TextButton(
        content=ft.Text("00:00:00", size=24),
        on_click=lambda e: playPause(e),
        offset=ft.Offset(0.1)
    )

    pokemonList = ft.ListView(
        spacing=10,
        padding=20,
        expand=True,
        controls=[]
    )

    def tabChange(e):
        nonlocal play

        save()
        if e.control.selected_index == 1 and activeTile:
            play = False
            activeTile.title = ft.Text(
                f"{activeHunt} - {pokemonDictionary[activeHunt][SRCOUNT]}", 
                size=20
            )
            activeTile.update()
    
    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Tabs(
                selected_index=0,
                length=2,
                expand=True,
                on_change=tabChange,
                content=ft.Column(
                    expand=True,
                    controls=[
                        ft.TabBar(
                            tabs=[
                                ft.Tab(label="Hunt"),
                                ft.Tab(label="Set"),
                            ]
                        ),
                        ft.TabBarView(
                            expand=True,
                            controls=[
                                ft.Container(
                                    ft.Column(
                                        [
                                            ft.Container(expand=1),
                                            ft.Column(
                                                [
                                                    ft.Row(
                                                        [
                                                            ft.Container(
                                                                content=
                                                                spriteContent,

                                                                alignment=
                                                                CENTER,
                                                                expand=1,

                                                                offset=
                                                                ft.Offset(
                                                                    0, -1 / 100
                                                                ), 
                                                            ),
                                                            numberContainer
                                                        ],
                                                        spacing=0
                                                    ),
                                                    ft.Container(height=50),
                                                    ft.Row(
                                                        [
                                                            addButton,
                                                            subtractButton
                                                        ],
                                                        spacing=0
                                                    ),
                                                ],
                                                alignment=AXIS_CENTER,

                                                horizontal_alignment=
                                                CROSS_AXIS_CENTER,

                                            ),
                                            ft.Container(expand=3),

                                            ft.Row(
                                                [
                                                    ft.Container(
                                                        content=ft.Text(
                                                            "Now Hunting:",
                                                            size=24
                                                        ),
                                                        expand=1,
                                                        alignment=BOTTOM_LEFT
                                                    ),
                                                    ft.Container(
                                                        content=activeHuntText
                                                    )
                                                ]
                                            ),

                                            ft.Row(
                                                [
                                                    ft.Container(
                                                        content=ft.Text(
                                                            "Time:",
                                                            size=24
                                                        ),
                                                        expand=1,
                                                        alignment=BOTTOM_LEFT
                                                    ),
                                                    playButton
                                                ]
                                            ),

                                            ft.Row(
                                                [
                                                    ft.Container(
                                                        content=ft.Text(
                                                            "Probability:",
                                                            size=24
                                                        ),
                                                        expand=1,
                                                        alignment=BOTTOM_LEFT
                                                    ),
                                                    probabilityContainer
                                                ]
                                            ),
                                            ft.Row(
                                                [
                                                    ft.Container(
                                                        content=ft.Text(
                                                            "P(x >= 1):",
                                                            size=24
                                                        ),
                                                        expand=1,
                                                        alignment=BOTTOM_LEFT
                                                    ),
                                                    ft.Container(
                                                        content=binomialText,
                                                        expand=1,
                                                        alignment=BOTTOM_RIGHT
                                                    )
                                                ]
                                            )
                                        ],
                                        expand=True,
                                        spacing=0
                                    )
                                ),
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Row(
                                                [
                                                    searchInput,
                                                    searchButton,
                                                ],
                                                alignment=ft.MainAxisAlignment.CENTER
                                            ),
                                            ft.Container(
                                                content=pokemonList,
                                                expand=True
                                            )
                                        ],
                                        expand=True
                                    ),
                                    padding=10
                                )
                            ]
                        )
                    ]
                )
            )
        )
    )

    update()
    filterPokemon()

ft.run(main, assets_dir="assets")