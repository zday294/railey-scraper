app.component('cabin-price', {
    props: {
        price: {
            required: true
        },
        bestPrice: {
            required: true
        }
    },
    template:
    /*html*/
    `
    <td v-if="price == undefined" class='unavailable'>-</td>
    <td v-else :class="{ 'best-price': isBestPrice, available: !isBestPrice}" > {{'$'}}{{formatRate(price)}}</td>
    `,
    methods: {
        formatRate(value) {
            return parseFloat(value).toFixed(2);
        }
    },
    computed: {
        isBestPrice() {
            return this.price == this.bestPrice
        }
    }
})