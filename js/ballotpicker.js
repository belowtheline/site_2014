function BallotPickerCtrl($scope, $http, $location, $window) {
    var divisionPath = $location.path();
    if (divisionPath == "/ballotpicker.html") {
        divisionPath = $location.hash();
    }
    if (divisionPath.substr(0, 7) == '/editor') {
        divisionPath = divisionPath.substr(7);
    }

    var division = {};
    var state = {};

    $scope.divisionCandidates = [];
    $scope.divisionBallotOrder = [];
    $scope.stateCandidates = [];
    $scope.stateBallotOrder = [];
    $scope.parties = {};

    $scope.groups = [];
    $scope.groupBallotOrder = [];

    $scope.orderByGroup = true;

    var applyGroupOrdering = function() {
        $scope.stateCandidates = _.sortBy($scope.stateCandidates, function(candidate) {
            return _.indexOf($scope.groups, state.groups[candidate.group]);
        });
    };

    $scope.showOrderByCandidate = function() {
        applyGroupOrdering();
        $scope.orderByGroup = false;
    };

    $scope.showOrderByGroup = function() {
        if(
            !$scope.stateDirty() ||
            $window.confirm("Are you sure? You'll lose any changes you made to candidate ordering.")
        ) {
            $scope.resetState();
            $scope.orderByGroup = true;
        }
    };

    $scope.groupsDirty = function() {
        return !(_.isEqual($scope.groups, $scope.groupBallotOrder));
    };

    $scope.stateDirty = function() {
        return !(_.isEqual($scope.stateCandidates, $scope.stateBallotOrder));
    };

    $scope.divisionDirty = function() {
        return !(_.isEqual($scope.divisionCandidates, $scope.divisionBallotOrder));
    };

    $scope.resetGroups = function() {
        $scope.groups = $scope.groupBallotOrder.slice();
    };
    $scope.resetState = function() {
        $scope.stateCandidates = $scope.stateBallotOrder.slice();
    };
    $scope.resetDivision = function() {
        $scope.divisionCandidates = $scope.divisionBallotOrder.slice();
    };

    $scope.downloadPDF = function () {
        console.log("Here we go!");
        if ($scope.orderByGroup) {
          applyGroupOrdering();
        }

        console.log($scope.divisionCandidates);
        console.log($scope.stateCandidates);
        console.log($scope.groups);

        function makeTicket(order, ballotOrder) {
            var ticket = [];

            angular.forEach(ballotOrder, function (candidate, idx) {
                ticket.push(_.indexOf(order, candidate) + 1);
            });

            return ticket;
        }

        var division_ticket = makeTicket($scope.divisionCandidates,
                                         $scope.divisionBallotOrder);
        var senate_ticket = makeTicket($scope.stateCandidates,
                                       $scope.stateBallotOrder);

        console.log(division_ticket);
        console.log(senate_ticket);

        function make_input(name, value) {
            return '<input type="hidden" name="' + name + '" value="' + value + '"/>';
        }

        var form = '<form action="http://api.belowtheline.org.au/pdf" method="POST">' +
                    make_input('division', divisionPath.slice(1)) +
                    make_input('state', division.division.state.split('/')[1]) +
                    make_input('division_ticket', division_ticket.join(',')) +
                    make_input('senate_ticket', senate_ticket.join(',')) +
                    '</form>';
        $(form).appendTo('body').submit().remove();
    }

    $http.get('/division' + divisionPath + '.json').success(function(data) {
        division = data;
        $scope.divisionName = data.division.name
        $scope.divisionCandidates = data.candidates;
        $scope.divisionBallotOrder = data.candidates.slice();

        $http.get('/' + division.division.state + '.json').success(function(data) {
            state = data;
            $scope.stateCandidates = _.map(data.ballot_order, function(id) {
                return data.candidates[id];
            });
            $scope.stateBallotOrder = $scope.stateCandidates.slice();

            var groupNames = _.without(_.uniq(_.pluck($scope.stateCandidates, 'group')), 'UG');
            var ungroupedCandidates = _.where($scope.stateCandidates, { group: 'UG' });
            $scope.groups = _.map(groupNames, function(name) { return state.groups[name]; });
            angular.forEach(ungroupedCandidates, function(candidate, idx) {
              var newGroup = {
                name: candidate.first_name + ' ' + candidate.last_name,
              };
              if(candidate.party) {
                newGroup.parties = [ candidate.party ];
              }

              var newGroupName = 'UG' + (idx + 1);
              state.groups[newGroupName] = newGroup;
              $scope.groups = $scope.groups.concat(newGroup);
              candidate.group = newGroupName;
            });
            $scope.groupBallotOrder = $scope.groups.slice();

        });
    });

    $http.get('/parties.json').success(function(data) {
        $scope.parties = data;
    });

}
