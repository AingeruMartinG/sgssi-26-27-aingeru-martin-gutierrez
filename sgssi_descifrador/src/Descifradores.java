import java.nio.charset.StandardCharsets;
import java.security.Signature;
import java.util.*;
import java.util.regex.MatchResult;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import java.util.zip.DeflaterOutputStream;

public class Descifradores {

    public String descifrar_cesar(String input){
        StringBuilder resultado = new StringBuilder();
        input = input.toLowerCase();


       for (int i = 1; i<27; i++) {

           System.out.println("Clave actual:"+ i);


           for (int j = 0; j < input.length(); j++ ) {

               char act = input.charAt(j);
               if(act<='z' && act>='a'){
                   act = (char) (((act - 97 + i) % 26) + 97);
               }
               resultado.append(act);
           }

           System.out.println("El resultado es:" + resultado);
           resultado = new StringBuilder();
       }

        return resultado.toString();
    }

    public void descifrar_tabla_de_frecuencias(String input) throws IllegalArgumentException{
        //Hago un diccionario en el que meto las letras que están en el texto y la cantidad de veces que aparecen
        HashMap<Character, Integer> diccionario = new HashMap<>();

        int inputIndex = 0;

        //Escaneo el texto como bien he dicho antes
        while(inputIndex < input.length()){
            char actChar = input.charAt(inputIndex);
            boolean mayus = (actChar >= 'A' && actChar<='Z');
            if ((actChar >= 'a' && actChar <= 'z' )|| mayus){
                if(mayus){
                    actChar = (char) (actChar + 32);
                }
                //Es suficientemente obvio pero el getOrDefault crea una nueva entrada en caso de no estar ya la letra en el hashmap
                diccionario.put(actChar, diccionario.getOrDefault(actChar, 0) + 1);
            }

            inputIndex++;
        }

        //En este bucle se cuenta la cantidad de caracteres totales, obviando espacios
        int suma = this.calcular_suma(diccionario);


        Set<Character> keys = diccionario.keySet();

        //Antes de hacer nada hay que escanear bigramas, trigramas y tetragramas
        //En este caso voy a hacerlo medio básico y solo voy a escanear bigramas, y además unos pocos

        //búsqueda de bigramas
        //Si alguno no sabe de regex (yo tampoco sé mucho), básicamente miro si los grupos de dos letras están rodeados
        //de espacios, pero no me los zampo, para ello el (?<=\\s)

        //Esto usa java 9 (diría que MatchResult no está en java <9)
        List<String> resultados = Pattern.compile("(?<=\\s)\\p{L}{2}(?=\\s)")
                .matcher(input)
                .results()
                .map(MatchResult::group)
                .toList();

        //Hago otro mapa de frecuencias con la info de los bigramas
        HashMap<String, Integer> bigramas = new HashMap<>();
        for(String bigr:resultados){
            bigramas.put(bigr, bigramas.getOrDefault(bigr, 0) + 1);
        }

        //Inicializo una lista con los posibles valores de las letras que queden, inicialmente están todos
        //pero se les va a ir restando según se usen
        HashSet<Character> posibles = new HashSet<>(diccionario.keySet());
        for (char c = 'a'; c <= 'z'; c++) {
            posibles.add(c);
        }

        String[] lookUpTableBigr = {"de", "la", "en", "el", "un"};

        //Cojo el valor más grande y lo relaciono directamente con el bigrama más repetido, cinco veces
        for(int i = 0; i < 5; i++) {
            String max = Objects.requireNonNull(bigramas.entrySet()
                    .stream()
                    .max(Map.Entry.comparingByValue())
                    .map(Map.Entry::getKey)
                    .orElse(null));


            String max1 = String.valueOf(max.charAt(0));
            String max2 = String.valueOf(max.charAt(1));

            String r1 = String.valueOf(lookUpTableBigr[i].charAt(0));
            String r2 = String.valueOf(lookUpTableBigr[i].charAt(1));

            // Reemplazamos la primera letra y la segunda en todo el texto
            input = input.replaceAll(Pattern.quote(max1), r1);
            input = input.replaceAll(Pattern.quote(max2), r2);

            char cR1 = lookUpTableBigr[i].charAt(0);
            char cR2 = lookUpTableBigr[i].charAt(1);

            //Borro del diccionario las letras cifradas
            diccionario.remove(Character.toLowerCase(max.charAt(0)));
            diccionario.remove(Character.toLowerCase(max.charAt(1)));

            //Y borro de posibles las letras que se han usado (es decir, las descifradas)
            posibles.remove(cR1);
            posibles.remove(cR2);

            bigramas.remove(max);
        }
        Scanner mikulector = new Scanner(System.in);

        Iterator <Character> mikuIterador = keys.iterator();

        for(int i = 0; i<diccionario.keySet().toArray().length; i++){

            if(i==0){
                System.out.println();
                System.out.println("Texto actual: " + input);}

            char iteAct = mikuIterador.next();

            System.out.println();
            System.out.println("Letra: " + Character.toUpperCase(iteAct) + ". Cantidad de apariciones: " + diccionario.get(iteAct) +
                    ". Porcentaje: " + (double) 100*diccionario.get(iteAct)/suma);

            System.out.println("Letras posibles: " + posibles);


            //GPT-ada nivel dios esto, me da una pereza increíble ponerme a hacer esto ahora xd
            char cifradaMayus = Character.toUpperCase(iteAct);

            Set<String> palabrasConLetra = Pattern.compile("\\b\\p{L}*" + Pattern.quote(String.valueOf(cifradaMayus)) + "\\p{L}*\\b")
                    .matcher(input)
                    .results()
                    .map(MatchResult::group)
                    .collect(Collectors.toCollection(LinkedHashSet::new));

            System.out.println("Aparece en las palabras: " + palabrasConLetra);
            System.out.println("Introduzca la letra que crea que corresponde");
            //gracias gemini

            //En caso de que en el string haya mayúsculas, las pasamos a minúsculas
            //'A' = 65, 'Z' = 90, 'a' = 95, 'z' = 122
            if(iteAct>=95 && iteAct<=122) {
                iteAct = (char) (iteAct - 32);
            }

            //Con un regex filtro las letras que quiero reemplazar y con un replaceAll lo cambio por la primera letra
            // de lo que escriba el usuario

            char lineInput = Character.toLowerCase(mikulector.nextLine().charAt(0));
            //Si no es una letra se lanza una excepción
            if((lineInput<65 || (lineInput>90 && lineInput<95) || lineInput>122))
            {throw new IllegalArgumentException("Por favor, introduzca un carácter válido " +
                    "(cualquier letra, mayúscula o minúscula");}

            input = input.replaceAll(java.util.regex.Pattern.quote(String.valueOf(iteAct)), Character.toString(lineInput));

            Iterator<Character> posIte = posibles.iterator();

            boolean found = false;
            while (posIte.hasNext() && !found) {
                Character act = posIte.next();
                if (act.equals(lineInput)) {
                    posIte.remove();
                    found = true;
                }
            }
            System.out.println("Actualizando...");
            System.out.println();
            System.out.println("Texto actualizado: " + input);

        }



    }

    public void cifrar_descifrar_XOR(String text, String key)
    {

        text = text.replaceAll("\\s+", "");

        byte[] textBytes = text.getBytes();
        byte[] keyBytes = key.getBytes();
        byte[] resBytes = new byte[textBytes.length];
        for(int i = 0; i < textBytes.length; i++){
            resBytes[i] = (byte) (textBytes[i] ^ keyBytes[i]);
        }

        //Por alguna razón el texto no se mostraba de manera correcta ya que utf-8 no leía bien todos los bytes
        //Se puede cambiar la codificación o directamente pasarlo a base 64, que es lo que he hecho
        System.out.println("Texto actual cifrado: " + Base64.getEncoder().encodeToString(resBytes));
        for (int i = 0; i < keyBytes.length; i++) {
            resBytes[i] = (byte) (resBytes[i] ^ keyBytes[i]);
        }
        System.out.println("Texto descifrado: " + new String(resBytes));
    }


    public <T> int calcular_suma( Map<T, Integer> pHashMap){
        int suma = 0;
        for(Object i:pHashMap.keySet()){
            suma = suma + pHashMap.get(i);
        }
        return suma;
    }
}

