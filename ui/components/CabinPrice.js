app.component('cabin-price', {
    props: {
        price: {
            required: true
        },
        highestPrice: {
            required: true
        }
    },
    template:
    /*html*/
    `
    <td v-if="price == undefined" class='unavailable'>-</td>
    <td v-else :class="{ 'best-price': isHighestPrice, available: !isHighestPrice}" > {{'$'}}{{formatRate(price)}}</td>
    `,
    methods: {
        formatRate(value) {
            return parseFloat(value).toFixed(2);
        }
    },
    computed: {
        isHighestPrice() {
            return this.price == this.highestPrice
        }
    }
})