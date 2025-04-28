from geopy.distance import geodesic

class DistanceCalculator:
    """
    Calcula a matriz de distâncias entre as localizações usando a distância geodésica.
    """
    def calculate_distance_matrix(self, locations):
        """
        Calcula a matriz de distâncias entre as localizações.

        Args:
            locations (list): Lista de dicionários contendo 'Latitude' e 'Longitude' de cada local.

        Returns:
            list: Matriz de distâncias entre as localizações.
        """
        distance_matrix = []
        for i in range(len(locations)):
            row = []
            for j in range(len(locations)):
                if i == j:
                    row.append(0)
                else:
                    coord_i = (locations[i]['Latitude'], locations[i]['Longitude'])
                    coord_j = (locations[j]['Latitude'], locations[j]['Longitude'])
                    distance = geodesic(coord_i, coord_j).kilometers
                    row.append(distance)
            distance_matrix.append(row)
        return distance_matrix