function gameManagement(element, id) {
  const row = parseInt(id[0]) - 1;
  const col = parseInt(id[2]) - 1;
  const gameID = element.getAttribute("data-game-id");

  $.ajax({
    url: "/game/" + gameID + "/grid/get-attributes/",
    type: "GET",
    dataType: "json",
    success: function (response) {
      var gameAttributesObject = JSON.parse(response.game_attributes);
      var grid = response.grid;
      var player1Symbol = response.player1_symbol;
      var player2Symbol = response.player2_symbol;

      if (grid[row][col] == null) {
        var data = {
          row: row,
          col: col,
          value: gameAttributesObject.active_player,
          newActivePlayer:
            gameAttributesObject.active_player === gameAttributesObject.creator
              ? gameAttributesObject.player2
              : gameAttributesObject.creator,
        };

        $.ajax({
          url: "/update-grid/" + gameID + "/",
          type: "POST",
          contentType: "application/json",
          data: JSON.stringify(data),
          success: function (response) {
            if (response.success) {
              console.log("Grid value updated successfully");
              $(document).ready(function () {
                function updateTable() {
                  $.ajax({
                    type: "GET",
                    url: "/game/" + gameID + "/grid/get-data/",
                    success: function (data) {
                      updateTableWithData(data.gameGrid, data.activePlayer);
                      let winner = checkWinner(
                        data.gameGrid,
                        data.gridSize,
                        data.alignment
                      );
                      if (winner !== null) {
                        console.log("Le joueur " + winner + " a gagné !");
                        gameIsOver(winner)
                      }
                    },
                    error: function (error) {
                      console.error("Error:", error);
                    },
                  });
                }

                function updateCellValue(cellId, newValue) {
                  var cell = document.getElementById(cellId);
                  if (cell) {
                    cell.innerHTML = newValue;
                  }
                }

                function updateTableWithData(gameGrid, activePlayer) {
                  for (var i = 0; i < gameGrid.length; i++) {
                    for (var j = 0; j < gameGrid[i].length; j++) {
                      var cellId = i + 1 + "-" + (j + 1);
                      var cellValue = gameGrid[i][j];
                      if (cellValue == gameAttributesObject.creator) {
                        cellValue = `<img src="${player1Symbol}">`;
                      } else if (cellValue == gameAttributesObject.player2) {
                        cellValue = `<img src="${player2Symbol}">`;
                      }
                      updateCellValue(cellId, cellValue);
                    }
                  }
                  $("#active-player").text("Au tour de " + activePlayer);
                }
                function checkWinner(grid, gridSize, alignment) {
                  // Vérification des row
                  for (let i = 0; i < gridSize; i++) {
                    let row = grid[i][0];
                    let count = 1;
                    for (let j = 1; j < gridSize; j++) {
                      if (grid[i][j] !== null && grid[i][j] === row) {
                        count++;
                        if (count === alignment) {
                          return row;
                        }
                      } else {
                        row = grid[i][j];
                        count = 1;
                      }
                    }
                  }

                  // Vérification des colonnes
                  for (let i = 0; i < gridSize; i++) {
                    let col = grid[0][i];
                    let count = 1;
                    for (let j = 1; j < gridSize; j++) {
                      if (grid[j][i] !== null && grid[j][i] === col) {
                        count++;
                        if (count === alignment) {
                          return col;
                        }
                      } else {
                        col = grid[j][i];
                        count = 1;
                      }
                    }
                  }

                  // Vérification des diagonales
                  for (let i = 0; i <= gridSize - alignment; i++) {
                    for (let j = 0; j <= gridSize - alignment; j++) {
                      let diagonal = grid[i][j];
                      let count = 1;
                      for (let k = 1; k < alignment; k++) {
                        if (
                          grid[i + k][j + k] !== null &&
                          grid[i + k][j + k] === diagonal
                        ) {
                          count++;
                          if (count === alignment) {
                            return diagonal;
                          }
                        } else {
                          break;
                        }
                      }
                    }
                  }

                  for (let i = 0; i <= gridSize - alignment; i++) {
                    for (let j = gridSize - 1; j >= alignment - 1; j--) {
                      let diagonal = grid[i][j];
                      let count = 1;
                      for (let k = 1; k < alignment; k++) {
                        if (
                          grid[i + k][j - k] !== null &&
                          grid[i + k][j - k] === diagonal
                        ) {
                          count++;
                          if (count === alignment) {
                            return diagonal;
                          }
                        } else {
                          break;
                        }
                      }
                    }
                  }

                  // Aucun gagnant trouvé
                  return null;
                }

                function gameIsOver(winner) {
                  $.ajax({
                      type: "GET",
                      url: "/game/over/" + winner + "/", 
                      success: function (data) {
                          console.log("La partie est terminée.");
                          window.location.href = "/game/over/" + winner + "/";
                      },
                      error: function (error) {
                          console.error("Erreur lors de la requête AJAX :", error);
                          // Gérer les erreurs si nécessaire
                      }
                  });
              }

                setInterval(updateTable, 1000);
              });
            } else {
              alert("Error updating grid value:", response.error);
            }
          },
          error: function (xhr, status, error) {
            console.log(error);
          },
        });
      }
    },
    error: function (error) {
      console.log(
        "Erreur lors de la récupération de la valeur de mon_attribut:",
        error
      );
    },
  });
}
