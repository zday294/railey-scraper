const app = Vue.createApp({
    data() {
        return {
            cabins: [
                {
                    name: "Alpine Lodge",
                    prices: {
                        "w3": 2040.50,
                        "w4": 1947.00
                    },
                    url: "https://www.deepcreek.com/vacation-rentals/alpine-lodge",
                    occupancy: 14,
                    upperBeds: 2,
                    mainBeds: 2,
                    lowerBeds: 2,
                    garageBeds: 0,
                    amenities: [
                        'Pool Table'
                    ],
                    score: 3810
                },
                {
                    name: "Into The Woods",
                    prices: {
                        "w3": 3088.80,
                        "w4": 2919.40
                    },
                    url: "https://www.deepcreek.com/vacation-rentals/woods",
                    occupancy: 14,
                    upperBeds: 3,
                    mainBeds: 1,
                    lowerBeds: 0,
                    garageBeds: 1,
                    amenities: [
                        'Pool',
                        'Home Theater'
                    ],
                    score: 2981
                },
                {
                    name: "Heavenly Haven",
                    prices: {
                        "w4": 2430.70
                    },
                    url: "https://www.deepcreek.com/vacation-rentals/heavenly-haven",
                    occupancy: 14,
                    upperBeds: 3,
                    mainBeds: 1,
                    lowerBeds: 2,
                    garageBeds: 0,
                    amenities: [
                        'Pool Table'
                    ],
                    score: 3520
                },
                {
                    name: "Captain Jack's",
                    prices: {
                        "w4": 2430.70
                    },
                    url: "https://www.deepcreek.com/vacation-rentals/captain-jacks",
                    occupancy: 14,
                    upperBeds: 3,
                    mainBeds: 1,
                    lowerBeds: 1,
                    garageBeds: 0,
                    amenities: [
                        'Pool Table'
                    ],
                    score: 2340
                },
                {
                    name: "Altitude Adjustment",
                    prices: {
                        "w4": 3457.30
                    },
                    url: "https://www.deepcreek.com/vacation-rentals/altitude-adjustment",
                    occupancy: 14,
                    upperBeds: 3,
                    mainBeds: 1,
                    lowerBeds: 1,
                    garageBeds: 0,
                    amenities: [
                        'Pool',
                        'Pool Table'
                    ],
                    score: 2593
                }
            ]
        }
    }
})