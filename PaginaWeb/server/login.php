<?php
session_start(); // Iniciar sesión

// Conexión a la base de datos
$servername = "localhost";
$dbUsername = "root";   // Cambia según tu configuración
$dbPassword = "12345678"; // Cambia según tu configuración
$dbname = "netcontrol";

try {
    $pdo = new PDO("mysql:host=$servername;dbname=$dbname;charset=utf8", $dbUsername, $dbPassword);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Verificar que se recibieron datos del formulario
    if (isset($_POST['correo']) && isset($_POST['contraseña'])) {
        $correo = filter_var($_POST['correo'], FILTER_SANITIZE_EMAIL);
        $contraseña = $_POST['contraseña'];

        // Verificar si el usuario existe
        $stmt = $pdo->prepare("SELECT id, correo, contraseña FROM usuarios WHERE correo = :correo");
        $stmt->bindParam(":correo", $correo);
        $stmt->execute();

        if ($stmt->rowCount() > 0) {
            $usuario = $stmt->fetch(PDO::FETCH_ASSOC);

            // Verificar la contraseña
            if (password_verify($contraseña, $usuario['contraseña'])) {
                $_SESSION['usuario_id'] = $usuario['id'];
                $_SESSION['correo'] = $usuario['correo'];

                // Redirigir al inicio
                header("Location: PaginaWeb/Paginas/inicio.html");
                exit();
            } else {
                echo "<script>alert('Contraseña incorrecta'); window.location.href='../index.html';</script>";
            }
        } else {
            echo "<script>alert('El usuario no existe'); window.location.href='../index.html';</script>";
        }
    } else {
        echo "<script>alert('Por favor, completa todos los campos'); window.location.href='../index.html';</script>";
    }
} catch (PDOException $e) {
    echo "<script>alert('Error de conexión: " . $e->getMessage() . "'); window.location.href='../index.html';</script>";
}

// Cerrar conexión
$pdo = null;
?>
