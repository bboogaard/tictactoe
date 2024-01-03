class PlayerProvider {

    constructor(settings) {
        this.gameHandlerUrl = settings.gameHandlerUrl;
        this.isActivePlayer = false;
    }

    init(board)  {
        let self = this;

        this.board = board;
        this.board.on('click', '.board-cell', function (event) {
            if (!self.isActivePlayer) {
                return;
            }
            let cell_id = $(this).attr('id');
            let parts = cell_id.split('-');
            self.isActivePlayer = false;
            self.addSymbol([parseInt(parts[1], 10), parseInt(parts[2], 10)]);
        });
    }

    pollGame() {
        let self = this;

        $.get(this.gameHandlerUrl)
            .done(function (res) {
                self.checkGameStatus(res);
            });
    }

    addSymbol(coords) {
        let self = this;

        $.ajax({
            type: "POST",
            url: this.gameHandlerUrl,
            dataType: 'json',
            async: true,
            headers: {
                "Content-Type": "application/json"
            },
            data: JSON.stringify({coords: coords}),
            success: function (res) {
                self.checkGameStatus(res);
            },
            error: function (xhr, ajaxOptions, thrownError) {
                self.isActivePlayer = true;
            }
        });
    }

    checkGameStatus(response) {
        this.updateBoard(response.board);
        this.isActivePlayer = response.isActivePlayer;
        if (response.isEnded) {
            this.onGameEnd(response);
        }
    }

    clearBoard() {
        this.board.find('.board-cell').text('');
    }

    updateBoard(board) {
        if (board === null) {
            return;
        }

        for (let i=0; i<board.length; i++) {
            for (let ii = 0; ii<board[i].length; ii++) {
                if (board[i][ii] !== null) {
                    this.board.find('#cell-' + i + '-' + ii).text(board[i][ii]);
                }
            }
        }
    }

    onGameEnd(response) {
        this.board.find('#owner-score').text(response.scores.owner);
        this.board.find('#opponent-score').text(response.scores.opponent);
    }

}

class OwnerProvider extends PlayerProvider {

    constructor(settings) {
        super(settings);
        this.sessionHandlerUrl = settings.sessionHandlerUrl;
        this.isReady = settings.isReady;
        this.isActive = settings.isActive;
        this.pollSessionProcess = null;
        this.pollGameProcess = null;
    }

    init(board) {
        super.init(board);

        let self = this;

        if (!this.isReady) {
            this.pollSessionProcess = setInterval(function () {
                self.pollSession();
            }, 5000);
        }

        if (this.isActive) {
            this.pollGame();
            this.pollGameProcess = setInterval(function () {
                self.pollGame();
            }, 5000);
        }

        this.board.on('click', '#start', function () {
            $(this).prop('disabled', true);
            self.clearBoard();
            $.post(self.sessionHandlerUrl)
                .done(function () {
                    self.pollGame();
                    self.pollGameProcess = setInterval(function () {
                        self.pollGame();
                    }, 5000);
                });
        });

    }

    pollSession() {
        let self = this;

        $.get(this.sessionHandlerUrl)
            .done(function (res) {
                if (res.isReady) {
                    clearInterval(self.pollSessionProcess);
                    self.board.find('#start').prop('disabled', false);
                    self.board.find('#invite').hide();
                }
            });
    }

    onGameEnd(response) {
        super.onGameEnd(response);
        if (response.winner) {
            alert(response.winner + ' won!');
        }

        clearInterval(this.pollGameProcess);
        this.board.find('#start').prop('disabled', false);
    }

}

class OpponentProvider extends PlayerProvider {

    constructor(settings) {
        super(settings);
        this.isIdle = true;
    }

    init (board) {
        super.init(board);

        let self = this;

        self.pollGame();
        setInterval(function () {
            self.pollGame();
        }, 5000);
    }

    checkGameStatus(response) {
        if (response.numSymbols === 1 && this.isIdle) {
            alert('New game started!');
            this.clearBoard();
            this.isIdle = false;
        }
        super.checkGameStatus(response);
    }

    onGameEnd(response) {
        super.onGameEnd(response);
        if (response.winner && !this.isIdle) {
            alert(response.winner + ' won!');
        }
        this.isIdle = true;
    }

}
