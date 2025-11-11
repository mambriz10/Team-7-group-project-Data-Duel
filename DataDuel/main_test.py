import Person

if __name__ == "__main__":
    test_person = Person.Person()
    test_person.populate_player_activities_by_day()
    test_person.sum_activities()

    print("passed api")
    print("\n\n")
    print(test_person.average_speed)
    print(test_person.baseline_average_speed)
    print(test_person.max_speed)
    print(test_person.baseline_max_speed)
    print(test_person.distance)
    print(test_person.baseline_distance)
    print(test_person.moving_time)
    print(test_person.baseline_moving_time)



    test_person.score.calculate_score(test_person.average_speed, test_person.max_speed, test_person.distance, test_person.moving_time,
                                      test_person.baseline_average_speed, test_person.baseline_max_speed, test_person.baseline_distance, test_person.baseline_moving_time,
                                      test_person.badges.get_points(), test_person.weekly_challenges.get_points(), test_person.streak)


    print(test_person.score.score)