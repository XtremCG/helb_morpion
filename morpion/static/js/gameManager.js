var grid, activePlayer, player1, player2, winner, gameID, row, col, abandon;
if ($("#game-board").length) {
  var gameAttributes = $("td").attr("data-game-attributes");
  var gameAttributesObject = JSON.parse(gameAttributes);
  var player1Symbol = $("td").attr("data-symbol-player1");
  var player2Symbol = $("td").attr("data-symbol-player2");
  var activePlayer = gameAttributesObject.active_player;
  var grid = gameAttributesObject.grid;
  gameID = gameAttributesObject.id;
  player1 = gameAttributesObject.creator;
  player2 = gameAttributesObject.player2;
  winner = null;
  abandon = null;

  $(document).ready(function () {
    setInterval(function () {
      if (abandon == null) {
        updateTable();
      } else {
        window.location.href = "/";
      }
    }, 800);
  });
}

function gameManagement(element) {
  row = parseInt(element.id[0]) - 1;
  col = parseInt(element.id[2]) - 1;
  if(grid[row][col] == null) {
    if (player2 == player1) {
      alert("Veuillez attendre que le deuxième joueur rejoigne la partie !");
    } else {
      updateGrid(abandon);
    }
  } else {
    alert("Vous ne pouvez pas cliquer sur cette case")
  }

}

function setAbandon(user) {
  var data = {
    abandonPlayer: user,
  }
  $.ajax({
    url: '/game/set-abanbon/' + gameID + '/',
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify(data),
    success: function (response) {
      if (response.success) {
        console.log("Abandon value updated successfully");
      } else {
        console.log(response.error);
      }
    },
    error: function (xhr, status, error) {
      console.log(error);
    },
  });
}

function updateGrid() {
  var data = {
    row: row,
    col: col,
    value: activePlayer,
    newActivePlayer: activePlayer === player1 ? player2 : player1,
  };

  $.ajax({
    url: "/update-grid/" + gameID + "/",
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify(data),
    success: function (response) {
      if (response.success) {
        console.log("Grid value updated successfully");
      } else {
        console.log(response.error);
      }
    },
    error: function (xhr, status, error) {
      console.log(error);
    },
  });
}

function updateTable() {
  $.ajax({
    type: "GET",
    url: "/game/" + gameID + "/grid/get-data/",
    success: function (response) {
      data = response.data;
      activePlayer = data.activePlayer;
      abandon = data.abandon;
      player2 = data.player2;
      player2Symbol = data.player2Symbol;
      updateTableWithData(data.gameGrid, data.activePlayer);
      winner = checkWinner(data.gameGrid, data.gridSize, data.alignment);
      if (winner !== null) {
        console.log("Le joueur " + winner + " a gagné !");
        gameOver();
      }
    },
    error: function (error) {
      console.error("Error:", error);
    },
  });
}

function gameOver() {
  $.ajax({
    type: "GET",
    url: "/game/" + gameID + "/over/" + winner + "/",
    success: function (data) {
      window.location.href = "/game/" + gameID + "/over/" + winner + "/";
    },
    error: function (error) {
      console.error("Erreur lors de la requête AJAX :", error);
    },
  });
}

function checkWinner(grid, gridSize, alignment) {
  for (let i = 0; i < gridSize; i++) {
    let row = grid[i][0];
    let count = 1;
    for (let j = 1; j < gridSize; j++) {
      if (grid[i][j] !== null && grid[i][j] === row) {
        count++;
        if (count === alignment) {
          return row; // Victoire
        }
      } else {
        row = grid[i][j];
        count = 1;
      }
    }
  }

  for (let i = 0; i < gridSize; i++) {
    let col = grid[0][i];
    let count = 1;
    for (let j = 1; j < gridSize; j++) {
      if (grid[j][i] !== null && grid[j][i] === col) {
        count++;
        if (count === alignment) {
          return col; // Victoire
        }
      } else {
        col = grid[j][i];
        count = 1;
      }
    }
  }

  for (let i = 0; i <= gridSize - alignment; i++) {
    for (let j = 0; j <= gridSize - alignment; j++) {
      let diagonal = grid[i][j];
      let count = 1;
      for (let k = 1; k < alignment; k++) {
        if (grid[i + k][j + k] !== null && grid[i + k][j + k] === diagonal) {
          count++;
          if (count === alignment) {
            return diagonal; // Victoire
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
        if (grid[i + k][j - k] !== null && grid[i + k][j - k] === diagonal) {
          count++;
          if (count === alignment) {
            return diagonal; // Victoire
          }
        } else {
          break;
        }
      }
    }
  }

  // Vérifier s'il y a des cases vides
  for (let i = 0; i < gridSize; i++) {
    for (let j = 0; j < gridSize; j++) {
      if (grid[i][j] === null) {
        return null;
      }
    }
  }

  return "Match nul"; // Aucune case vide, match nul
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
      if (cellValue == player1) {
        cellValue = `<img src="${player1Symbol}" alt="">`;
      } else if (cellValue == player2) {
        cellValue = `<img src="${player2Symbol}" alt="">`;
      }
      updateCellValue(cellId, cellValue);
    }
  }
  $("#player2").text("Joueur 2 : " + player2);
  if (player2 == player1) {
    $("#player2").text("En attente du deuxième joueur...");
  }
  $("#active-player").text("Au tour de " + activePlayer);
}
