(function( $ ) {

    class TicTacToeApi {
        constructor(settings) {
            this.board = settings.board;
            this.provider = settings.provider;
        }

        init() {
            this.provider.init(this.board);
        }
    }

    $.fn.ticTacToe = function(settings) {

        let ticTacToeApi = new TicTacToeApi({
            board: $(this),
            provider: settings.provider
        });
        ticTacToeApi.init();

        return this;

    };

}( jQuery ));