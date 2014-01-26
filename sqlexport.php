<?php
/**
 * Script that adds a basic API to extract MySQL table data for backup reason,
 * and later reconstruction of the database.
 *
 * @author Daniel "MaTachi" Jonsson
 */

// Authentication.
//
// The $sha256_api_key is a sha256 hash of the API key.
//
// First, generate a key, for example with:
//    $ cat /dev/urandom | tr -dc A-Za-z0-9 | head -c 50; echo
//
// Then, calculate the sha256 hash sum of the key, for example with:
//    $ echo -n APIKEY | sha256sum
$sha256_api_key = "SHA256_OF_APIKEY";
if (hash("sha256", $_GET["key"]) !== $sha256_api_key) {
  exit();
}

// Try to import WordPress's config file where database settings is already
// stored.
if (file_exists("wp-config.php")) {
  include_once("wp-config.php");
} else {
  define('DB_NAME', 'database_name');
  define('DB_USER', 'user');
  define('DB_PASSWORD', 'password');
  define('DB_HOST', 'localhost');
  define('DB_CHARSET', 'utf8');
}

// Function that returns the first element from an array.
$grab_first_element = function($array) {
  return $array[0];
};

// Init MySQL
$mysqli = new mysqli(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME);
if ($mysqli->connect_errno) {
  printf("Connect failed: %s\n", $mysqli->connect_error);
  exit();
}

// Set encoding
if (!$mysqli->set_charset(DB_CHARSET)) {
  printf("Error loading character set utf8: %s\n", $mysqli->error);
  exit();
}

/**
 * Return an array of the names of the tables in the database.
 *
 * @return array An array of the names of the tables in the database.
 */
function table_names() {
  global $mysqli, $grab_first_element;
  $res = $mysqli->query("SHOW TABLES");
  $tables = array_map($grab_first_element, $res->fetch_all());
  $res->close();
  return $tables;
}

/**
 * Return an array of CREATE TABLE statements, one for each table in the
 * databaase.
 *
 * @return array An array of statements to construct the database tables.
 */
function create_table_statements() {
  global $mysqli;
  $create_tables = array();
  $table_names = table_names();
  foreach ($table_names as $table) {
    $res = $mysqli->query(sprintf("SHOW CREATE TABLE %s", $table));
    $row = $res->fetch_row();
    $create_table = sprintf("%s;", $row[1]);
    $res->close();
    array_push($create_tables, $create_table);
  }
  return $create_tables;
}

/**
 * Returns an INSERT INTO string.
 *
 * @param array $args Element "limit" is an SQL LIMIT. For example "100, 50".
 *                    Element "table" is the table data should be extracted
 *                    from.
 * @return string An INSERT INTO statement with values specified by the param
 *                limit.
 */
function insert_into_statements($args) {
  $limit = isset($args["limit"]) ? $args["limit"] : "0, 100";
  $table = isset($args["table"]) ? $args["table"] : "wp_posts";
  global $mysqli, $grab_first_element;

  $res = $mysqli->query(sprintf("SHOW COLUMNS FROM %s", $table));
  $fields = array_map($grab_first_element, $res->fetch_all());
  $res->close();
  $field_list = implode("`, `", $fields);

  $sql = sprintf("SELECT * FROM %s LIMIT %s", $table, $limit);
  $insert_into = "INSERT INTO `%s` (`%s`) VALUES\n('%s');";
  if ($res = $mysqli->query($sql)) {
    $values = array();
    while ($row = $res->fetch_row()) {
      $values_row = array();
      foreach ($row as $value) {
        array_push($values_row, addslashes($value));
      }
      $values_row = implode("', '", $values_row);
      array_push($values, $values_row);
    }
    $values = implode("'),\n('", $values);
    $insert_into = sprintf($insert_into, $table, $field_list, $values);
  }
  return $insert_into;
}

/**
 * Count the rows in a given table.
 *
 * @param array $args Element "table" is the table whose rows should be
 *                    counted.
 * @return integer The number of rows in the table.
 */
function count_rows($args) {
  global $mysqli;
  $table = isset($args["table"]) ? $args["table"] : "wp_posts";
  $res = $mysqli->query(sprintf("SELECT COUNT(*) AS rows FROM %s", $table));
  $row = $res->fetch_array();
  $rows = (int) $row["rows"];
  $res->close();
  return $rows;
}

// The functions that can be executed from the API, for example:
// ?key=...&function=tables
$functions = array(
  "tables" => "table_names",
  "create_tables" => "create_table_statements",
  "insert_into" => "insert_into_statements",
  "count_rows" => "count_rows",
);

// Extract the optional args from the URL.
$args = $_GET;
unset($args["key"]);
unset($args["function"]);

header("Content-Type: application/json");
print(json_encode($functions[$_GET["function"]]($args)));
