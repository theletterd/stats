from models import GoogleFitData

class GoogleFitStats(object):

    # so this is presumably where we should be collecting our stats from.
    def get_stats():
        pass


    def get_stats_for_year(year):
        data = GoogleFitData.get_data_for_year(year)

        steps = 0
        weights = []
        distance = 0

        for datapoint in data:
            steps += datapoint.step_count
            distance += datapoint.distance_metres

            if datapoint.weight_kg:
                weights.append(datapoint.weight_kg)


        print(min(weights))
        print(max(weights))
        print(sum(weights) / len(weights))

        # from this, we can get min/max/average weight
        # and total steps, total distance

        return int(steps), float(distance)

    def get_most_recent_weight():
        pass

    def get_recent_stats():
        # steps yesterday
        # steps today

        # steps last week
        # steps this week so far

        # average weekly steps

        # distance yesterday
        # distance today

        # distance last week
        # distance this week
        # average weekly distance

        pass
