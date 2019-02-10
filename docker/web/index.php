<html>
    <head>
        <title>RPG Sim</title>
    </head>

    <body>
        <h1>RPG Simulations</h1>
        <ul>
            <?php
            $json = file_get_contents('http://simrest/');
            $obj = json_decode($json);
            $gameSystems = $obj->gameSystems;
            foreach ($gameSystems as $gameSystem) {
                echo "<li>$gameSystem</li>";
            }
            ?>
        </ul>
    </body>
</html>