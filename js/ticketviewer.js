'use strict';

function TicketViewerCtrl($scope, $http, $location) {
    var state = $location.path();
    if (state == "/ticketviewer.html") {
        state = $location.hash();
    }
    if (state.substr(0, 7) == '/viewer') {
        state = state.substr(7);
    }

    $scope.ticket = [null, null];
    $scope.candidateOrder = [[], []];

    $scope.ticketList = [];

    $scope.changeTicket = function (idx) {
        if (!$scope.ticket[idx]) {
            $scope.candidateOrder[idx] = $scope.ballotOrder;
            return;
        }

        var data = $scope.ticket[idx].split('-');
        var group = data[0];
        var ticket = parseInt(data[1]) - 1;

        $scope.candidateOrder[idx] = $scope.groups[group].tickets[ticket];
    }

    function generateTicketList() {
        var groups = []
        var tickets = [];

        angular.forEach($scope.groups, function (group, group_id) {
            groups.push(group_id);
        });

        groups.sort(function (a, b) {
            if (a.length != b.length) {
                return a.length - b.length;
            } else if (a < b) {
                return -1
            } else if (b > a) {
                return 1;
            } else {
                return 0;
            }
        })

        angular.forEach(groups, function (group_id, idx) {
            var group = $scope.groups[group_id];

            if (group.tickets.length == 1) {
                tickets.push({
                    id: "" + group_id + "-1",
                    name: group.name
                });
            } else {
                angular.forEach(group.tickets, function (ticket, idx) {
                    tickets.push({
                        id: "" + group_id + "-" + (idx + 1),
                        name: group.name + " (" + (idx + 1) + " of " + group.tickets.length + ")"
                    });
                });
            }
        });

        $scope.ticketList = tickets;
    }

    $http.get('/state' + state + '.json').
        success(function (data) {
            $scope.state = data.state;
            $scope.stateOrTerritory = data.state_or_territory;
            $scope.candidates = data.candidates;
            $scope.ballotOrder = data.ballot_order;
            $scope.groups = data.groups;

            $scope.candidateOrder = [$scope.ballotOrder, $scope.ballotOrder];

            generateTicketList();
        }).
        error(function () {
            console.log("I have no idea");
        });
    $http.get('/parties.json').
        success(function (data) {
            $scope.parties = data;
        }).
        error(function () {
            console.log("I have no idea");
        });
}
