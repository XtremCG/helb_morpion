function gameManagement(element, id) {
  const row = parseInt(id[0]) - 1;
  const col = parseInt(id[2]) - 1;
  const gameID = element.getAttribute("data-game-id");
  
  $.ajax({
    url: "/game/" + gameID +"/grid/get-attributes/",
    type: "GET",
    dataType: "json",
    success: function (response) {
      var gameAttributesObject = JSON.parse(response.game_attributes);
      var grid = response.grid
      var player1Symbol = response.player1_symbol
      var player2Symbol = response.player2_symbol
      console.log(gameAttributesObject)
      console.log(grid);

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
            } else {
              console.error("Error updating grid value:", response.error);
            }
          },
          error: function (xhr, status, error) {
            console.error("AJAX request failed:", status, error);
          },
        });

        if (gameAttributesObject.active_player === gameAttributesObject.creator) {
          element.innerHTML = '<img src="' + player1Symbol + '" alt="Player 1">';
        } else if (
          gameAttributesObject.active_player === gameAttributesObject.player2
        ) {
          element.innerHTML = '<img src="' + player2Symbol + '" alt="Player 2">';
        }
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
