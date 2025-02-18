<?php
session_start();

// Configuración de la conexión con PDO
$dsn = 'mysql:host=localhost;dbname=tu_basedatos;charset=utf8';
$usuarioDB = 'root';
$contraseñaDB = '12345678';

try {
    $pdo = new PDO($dsn, $usuarioDB, $contraseñaDB);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("Error de conexión: " . $e->getMessage());
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Recibe los datos del formulario
    $correo = $_POST['correo'];
    $contraseñaIngresada = $_POST['contraseña'];

    // Consulta para obtener el usuario por correo
    $stmt = $pdo->prepare("SELECT * FROM usuarios WHERE correo = ?");
    $stmt->execute([$correo]);
    $usuario = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($usuario) {
        echo "If de usuario";
        // Verifica la contraseña utilizando password_verify
        if (password_verify($contraseñaIngresada, $usuario['contraseña'])) {
            echo "paso la verifiacion";
            // Opcional: almacenar datos en la sesión
            $_SESSION['usuario'] = $usuario;

            // Redirecciona a ../Paginas/inicio.html
            header("Location: ../Paginas/inicio.html");
            exit(); // Termina la ejecución para asegurarte de que no se ejecute más código
        } else {
            echo "Contraseña incorrecta.";
        }
    } else {
        echo "El usuario no existe.";
    }
}
?>
